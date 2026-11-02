"""CN-only entry points, input boundaries and failure semantics (no network)."""
import json
from pathlib import Path
import pytest
from engi_agent.engineering.cn_schema import TaskRequest, ParameterValue, EngineeringState
from engi_agent.engineering.cn_schema import CNProfile
from engi_agent.engineering.roles import FixtureRoles
from engi_agent.engineering.cn_workflow import prepare, confirm, run_engineering, stamp, normalize
from engi_agent.engineering.cn_presentation import save_reports

ROOT = Path(__file__).resolve().parents[1]


def request(name="cn_design"):
    return TaskRequest.model_validate_json((ROOT / "examples/engineering" / f"{name}.json").read_text(encoding="utf-8"))


def run(r):
    return run_engineering(confirm(prepare(r)), FixtureRoles(r))


def test_omitted_code_uses_cn_materials_loads_and_all_five_checks():
    raw = request().model_dump(); raw.pop("code"); raw.pop("targets")
    r = TaskRequest.model_validate(raw)
    s = run(r)
    assert r.code == "cn-2024" and isinstance(s.profile, CNProfile)
    assert s.tool_results["evaluation.materials"].outputs["fc_mpa"] == 14.3
    assert s.tool_results["evaluation.load_combination"].outputs["ultimate_load_kn_m"] == pytest.approx(1.3 * 14.125 + 1.5 * 5)
    assert set(s.evaluation.checks) == {"flexure", "shear", "detailing", "crack", "deflection"}
    assert s.evaluation.status == "pass" and s.evaluation.overall_status == "incomplete"


@pytest.mark.parametrize("code", ["teaching", "aci", "ACI318-19", "eurocode", "", None])
def test_non_cn_request_codes_rejected(code):
    raw = request().model_dump(); raw["code"] = code
    with pytest.raises(ValueError): TaskRequest.model_validate(raw)


@pytest.mark.parametrize("targets", [["elastic_deflection"], ["flexure", "elastic_deflection"], [], ["flexure", "flexure"]])
def test_invalid_or_removed_targets_rejected(targets):
    raw = request().model_dump(); raw["targets"] = targets
    with pytest.raises(ValueError): TaskRequest.model_validate(raw)


@pytest.mark.parametrize("key,value,unit", [
    ("span_mm", "nan", "mm"), ("span_mm", "inf", "mm"),
    ("live_load_kn_m", True, "kN/m"), ("fc_mpa", 30, "MPa"),
    ("fy_mpa", 400, "MPa"), ("elastic_modulus_mpa", 30000, "MPa"),
    ("self_weight_mode", "ignore", None), ("span_mm", 20, "ft"),
])
def test_invalid_values_and_removed_field_conventions_rejected(key, value, unit):
    r = request(); r.parameters[key] = ParameterValue(value=value, unit=unit)
    with pytest.raises(ValueError): prepare(r)


def test_normalization_is_idempotent_and_preserves_input():
    r = request(); r.parameters["span_mm"] = ParameterValue(value=6, unit="m")
    normalized = normalize(r)
    assert normalize(normalized).model_dump() == normalized.model_dump()
    assert normalized.parameters["span_mm"].value == 6000
    assert normalized.parameters["span_mm"].raw_value == 6
    assert r.parameters["span_mm"].unit == "m"


def test_explicit_deflection_ratio_text_preserves_input_and_reference_results():
    r = request(); r.parameters['deflection_limit_ratio'] = ParameterValue(value='L/250')
    prepared = prepare(r)
    assert prepared.request.parameters['deflection_limit_ratio'].value == 250
    assert prepared.request.parameters['deflection_limit_ratio'].raw_value == 'L/250'
    assert run(r).tool_results['evaluation.deflection_check'].outputs == run(request()).tool_results['evaluation.deflection_check'].outputs
    from engi_agent.engineering.cn_presentation import parameter_rows
    row = next(row for row in parameter_rows(prepared) if row[2] == '挠度限值分母')
    assert row[3] == row[4] == 'L/250'


def test_unvalidated_copies_cannot_bypass_cn_contract():
    s = confirm(prepare(request()))
    s.request = s.request.model_copy(update={"code": "teaching"})
    s.confirmation_hash = stamp(s)  # A matching hash cannot authorize a foreign contract.
    class NoRoles:
        def plan(self, *args): raise AssertionError("role must not run")
    rejected = run_engineering(s, NoRoles())
    assert rejected.evaluation.status == "error" and not rejected.tool_results
    with pytest.raises(ValueError): prepare(s.request)
    with pytest.raises(ValueError): confirm(s)


def test_profile_and_request_assignments_cannot_switch_standard():
    r = request()
    with pytest.raises(ValueError): r.code = "teaching"
    raw = prepare(r).model_dump(); raw["profile"] = {"version": "teaching-rc-1"}
    with pytest.raises(ValueError): EngineeringState.model_validate(raw)
    s = confirm(prepare(r)); s.profile = s.profile.model_copy(update={"version": "foreign"})
    assert run_engineering(s, FixtureRoles(r)).evaluation.status == "error"


@pytest.mark.parametrize("changes", [{"version": "teaching-rc-1"}, {"gamma_dead": 1.2}, {"gamma_live": 1.6}])
def test_direct_cn_entry_points_reject_mutated_profiles(changes):
    r = request()
    s = confirm(prepare(r))
    s.profile = s.profile.model_copy(update=changes)
    s.confirmation_hash = stamp(s)
    with pytest.raises(ValueError): prepare(r, s.profile)
    with pytest.raises(ValueError): confirm(s)
    class NoRoles:
        def plan(self, *args): raise AssertionError("role must not run")
    rejected = run_engineering(s, NoRoles())
    assert rejected.evaluation.status == "error" and not rejected.tool_results


def test_direct_cn_confirmation_rejects_unsupported_even_with_complete_parameters():
    s = prepare(request())
    s.request.task_type = "unsupported"
    with pytest.raises(ValueError): confirm(s)


def test_missing_density_and_direct_design_load_conflict_cannot_confirm():
    r = request(); r.parameters.pop("concrete_unit_weight_kn_m3")
    with pytest.raises(ValueError): confirm(prepare(r))
    r = request(); r.parameters["design_moment_kn_m"] = ParameterValue(value=100, unit="kN·m")
    with pytest.raises(ValueError): confirm(prepare(r))


def test_query_shear_at_midspan_does_not_reduce_actual_design_demand():
    r = request(); r.parameters["shear_position_mm"] = ParameterValue(value=3000, unit="mm")
    s = run(r)
    assert s.tool_results["evaluation.beam_analysis"].outputs["Vu_at_position_kn"] == 0
    assert s.tool_results["evaluation.shear_check"].outputs["demand_kn"] > 0


def test_fixed_section_constraint_blocks_design_without_hidden_changes():
    r = request(); r.parameters["max_depth_mm"] = ParameterValue(value=400, unit="mm")
    s = run(r)
    assert s.evaluation.status == "fail" and not s.candidate
    assert s.tool_results["design.section_geometry"].status == "blocked"
    assert not any(k.startswith("evaluation.") for k in s.tool_results)


def test_evaluation_role_failure_after_design_cannot_retain_pass():
    r = request()
    class BadEvaluation(FixtureRoles):
        def plan(self, role, payload):
            if role == "Evaluation": raise TimeoutError("private provider message")
            return super().plan(role, payload)
    s = run_engineering(confirm(prepare(r)), BadEvaluation(r))
    assert s.candidate and s.evaluation.status == "error" and not any(s.evaluation.checks.values())
    assert "private provider message" not in str(s.errors)


def test_unsupported_task_cannot_confirm_or_execute():
    r = TaskRequest(task_type="unsupported")
    pending = prepare(r)
    with pytest.raises(ValueError): confirm(pending)
    s = run_engineering(pending, FixtureRoles(r))
    assert s.evaluation.status == "incomplete" and not s.tool_results


def test_cn_reports_round_trip_and_do_not_overwrite(tmp_path):
    s = run(request())
    md, data = save_reports(s, tmp_path); md2, _ = save_reports(s, tmp_path)
    assert md != md2 and md.exists()
    restored = EngineeringState.model_validate_json(data.read_text(encoding="utf-8"))
    assert restored == s and restored.profile.version == "cn-rc-2024-v1"
    text = md.read_text(encoding="utf-8")
    assert all(x in text for x in ("中国规范", "裂缝", "长期挠度", "输入哈希"))


def test_cli_rejects_foreign_file_even_with_cn_override(tmp_path, capsys):
    from engi_agent.engineering.cli import main
    raw = request().model_dump(); raw['code'] = 'teaching'
    source = tmp_path / 'foreign.json'
    source.write_text(json.dumps(raw), encoding='utf-8')
    output = tmp_path / 'reports'
    assert main(['--request', str(source), '--code', 'cn-2024', '--offline',
                 '--approve', '--output-dir', str(output)]) == 2
    assert not output.exists()
    assert '任务失败' in capsys.readouterr().out


def test_cli_rejects_removed_code_switch_before_execution():
    from engi_agent.engineering.cli import main
    with pytest.raises(SystemExit) as exc:
        main(['--code', 'teaching', '--request', 'unused.json', '--offline'])
    assert exc.value.code == 2
