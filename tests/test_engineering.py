"""Independent mechanics, boundary and workflow verification (no network)."""
import json
from pathlib import Path
import pytest

from engi_agent.engineering.schema import TaskRequest, ParameterValue, TeachingProfile, normalize
from engi_agent.engineering.roles import FixtureRoles, RolePlan
from engi_agent.engineering.workflow import prepare, confirm, run_engineering
from engi_agent.engineering.reporting import markdown_report, save_reports
from engi_agent.engineering.tools import REGISTRY

ROOT = Path(__file__).resolve().parents[1]


def request(name="paper_normal"):
    return TaskRequest.model_validate_json((ROOT / "examples" / "engineering" / f"{name}.json").read_text(encoding="utf-8"))


def change(r, key, value, unit=None):
    r.parameters[key] = ParameterValue(value=value, unit=unit)
    return r


def run(r):
    return run_engineering(confirm(prepare(r)), FixtureRoles(r))


def result(s, name, prefix="evaluation"):
    return s.tool_results[f"{prefix}.{name}"].outputs


def test_design_with_self_weight_and_independent_evaluation():
    s = run(request())
    assert s.evaluation.status == "pass"
    assert s.candidate["bar_count"] == 4
    assert s.evaluation.overall_status == "incomplete"
    assert s.evaluation.code_status == "未完成"
    # Design and evaluation each execute their own section/load/analysis tools.
    assert "design.beam_analysis" in s.tool_results and "evaluation.beam_analysis" in s.tool_results
    assert result(s, "flexural_check")["As_mm2"] == pytest.approx(4 * 645.16)
    assert [e["role"] for e in s.role_events] == ["Design", "Evaluation"]


def test_independent_hand_calculation_reference_without_self_weight():
    s = run(request("paper_ignore_self_weight"))
    loads = result(s, "load_combination")
    analysis = result(s, "beam_analysis")
    # Independent arithmetic in original units, not a fixture copied from OCR.
    expected_w_kip_ft = 1.2 * .82 + 1.6 * 1
    assert loads["ultimate_load_kn_m"] == pytest.approx(expected_w_kip_ft * 14.593902937206)
    assert analysis["Mu_kn_m"] == pytest.approx(expected_w_kip_ft * 25**2 / 8 * 1.35581794833)
    assert analysis["Vu_max_kn"] == pytest.approx(expected_w_kip_ft * 25 / 2 * 4.44822161526)
    assert s.candidate["bar_count"] == 3
    assert s.tool_results["evaluation.load_combination"].warnings


def test_self_weight_is_added_once_and_included_mode_reproduces_it():
    s = run(request())
    load = result(s, "load_combination")
    sw = 150 * (12 / 12) * (20 / 12) / 1000  # kip/ft
    assert load["self_weight_kn_m"] == pytest.approx(sw * 14.593902937206, rel=1e-9)
    r = request()
    change(r, "dead_load_kn_m", .82 + sw, "kip/ft")
    change(r, "self_weight_mode", "included")
    assert result(run(r), "load_combination")["ultimate_load_kn_m"] == pytest.approx(load["ultimate_load_kn_m"])


def test_effective_depth_spacing_and_actual_flexural_capacity():
    s = run(request("paper_ignore_self_weight"))
    g = result(s, "section_geometry")
    assert g["effective_depth_mm"] == pytest.approx((20 - 1.5 - .375 - 1.128/2) * 25.4)
    spacing = result(s, "detailing_check")
    # clear gap among 3 bars in the straight interior of the stirrup.
    assert spacing["clear_spacing_mm"] == pytest.approx((12 - 2*1.5 - 2*.375 - 3*1.128)/2 * 25.4)
    cap = result(s, "flexural_check")
    area, fy, fc, b, d = 3*645.16, 60*6.894757293168, 4.35*6.894757293168, 304.8, g["effective_depth_mm"]
    a = area*fy/(.85*fc*b)
    assert cap["capacity_kn_m"] == pytest.approx(.9*area*fy*(d-a/2)/1e6)


def test_elastic_deflection_independent_hand_solution():
    s = run(request())
    w = (0.82 + .25 + 1) * 14.593902937206
    L, E, I = 7620, 27568.7, 304.8*508**3/12
    assert result(s, "elastic_deflection")["deflection_mm"] == pytest.approx(5*w*L**4/(384*E*I))
    assert result(s, "elastic_deflection")["limit_mm"] == pytest.approx(7620/240)


def test_unsized_design_uses_sizing_tool():
    r = request("unsized_design")
    change(r, "live_load_kn_m", 0.6, "kip/ft")
    s = run(r)
    assert s.evaluation.status == "pass"
    assert s.candidate["beam_depth_mm"] == 500
    assert "beam_depth_mm" not in s.request.parameters


def test_unsized_paper_loads_can_fail_without_hidden_section_increase():
    s = run(request("unsized_design"))
    assert s.evaluation.status == "fail"
    assert result(s, "section_sizing", "design")["beam_depth_mm"] == 500
    assert not s.candidate


def test_existing_beam_fails_flexure_when_self_weight_is_counted():
    s = run(request("existing_beam"))
    assert s.evaluation.status == "fail"
    assert not result(s, "flexural_check")["pass"]
    assert not any(k.startswith("design.") for k in s.tool_results)


def test_flexure_only_skips_unrelated_checks_and_material_requirements():
    r = request("flexure_only")
    for key in ("elastic_modulus_mpa", "deflection_limit_ratio", "stirrup_fy_mpa", "stirrup_legs", "stirrup_spacing_mm"):
        del r.parameters[key]
    s = run(r)
    assert "evaluation.elastic_deflection" not in s.tool_results
    assert "evaluation.shear_check" not in s.tool_results
    assert "evaluation.flexural_check" in s.tool_results
    assert s.evaluation.overall_status == "incomplete"


def test_missing_load_blocks_confirmation_before_any_role_or_tool():
    r = request()
    del r.parameters["dead_load_kn_m"]
    s = prepare(r)
    assert "dead_load_kn_m" in s.missing_parameters
    with pytest.raises(ValueError):
        confirm(s)
    out = run_engineering(s, FixtureRoles(r))
    assert out.evaluation.status == "error" and not out.tool_results


@pytest.mark.parametrize("key,value,unit", [
    ("span_mm", -1, "m"), ("span_mm", "nan", "mm"),
    ("span_mm", 5, "kN/m"), ("fc_mpa", 5, "MPa"),
    ("bar_count", 2.5, None), ("live_load_kn_m", True, "kN/m"),
    ("support_type", "cantilever", None), ("unknown", 3, "mm"),
])
def test_bad_parameters_rejected(key, value, unit):
    with pytest.raises((ValueError, TypeError)):
        prepare(change(request(), key, value, unit))


def test_mixed_units_equivalent_and_normalization_is_idempotent():
    r = request()
    change(r, "span_mm", 7.62, "m")
    change(r, "elastic_modulus_mpa", 27.5687, "GPa")
    n = normalize(r)
    assert normalize(n).model_dump() == n.model_dump()
    assert result(run(r), "beam_analysis")["Mu_kn_m"] == pytest.approx(result(run(request()), "beam_analysis")["Mu_kn_m"])


def test_unconfirmed_and_changed_after_confirmation_rejected():
    r = request()
    s = confirm(prepare(r))
    s.request.parameters["live_load_kn_m"].value = 0.0
    out = run_engineering(s, FixtureRoles(r))
    assert out.evaluation.status == "error"
    assert not out.tool_results


def test_reduced_query_shear_does_not_reduce_design_demand():
    r = request()
    change(r, "shear_position_mm", 3810, "mm")
    s = run(r)
    assert result(s, "beam_analysis")["Vu_at_position_kn"] == 0
    assert result(s, "shear_check")["demand_kn"] > 0


def test_existing_widely_spaced_stirrups_fail():
    r = request("existing_beam")
    change(r, "stirrup_spacing_mm", 1000, "mm")
    assert not result(run(r), "shear_check")["pass"]


def test_elastic_exceedance_is_fail_and_no_automatic_redesign():
    r = request()
    change(r, "deflection_limit_ratio", 5000)
    s = run(r)
    assert s.evaluation.status == "fail"
    assert not result(s, "elastic_deflection")["pass"]
    assert len([k for k in s.tool_results if k == "design.flexural_design"]) == 1
    assert s.candidate["status"] == "rejected"


def test_infeasible_section_or_layout_blocks_design_descendants():
    r = request()
    change(r, "beam_width_mm", 140, "mm")
    s = run(r)
    assert s.evaluation.status == "fail"
    assert s.tool_results["design.shear_design"].status == "blocked"
    assert not any(k.startswith("evaluation.") for k in s.tool_results)


def test_maximum_dimension_constraint_is_enforced():
    r = request()
    change(r, "max_depth_mm", 400, "mm")
    s = run(r)
    assert s.evaluation.status == "fail"
    assert s.tool_results["design.section_geometry"].status == "blocked"


def test_tool_exception_blocks_dependency_and_cannot_pass(monkeypatch):
    def broken(*_):
        raise RuntimeError("internal error")
    monkeypatch.setitem(REGISTRY, "beam_analysis", broken)
    s = run(request())
    assert s.evaluation.status == "error"
    assert s.tool_results["design.flexural_design"].status == "blocked"


@pytest.mark.parametrize("bad", [{"Mu_kn_m": 1}, {"beam_width_mm": "300", "beam_depth_mm": 500, "sizing_basis": "wrong type"}])
def test_malformed_tool_output_is_rejected(monkeypatch, bad):
    monkeypatch.setitem(REGISTRY, "section_sizing", lambda *_: bad)
    s = run(request())
    assert s.evaluation.status == "error"
    assert s.tool_results["design.section_geometry"].status == "blocked"


def test_missing_self_weight_density_blocks_confirmation():
    r = request()
    del r.parameters["concrete_unit_weight_kn_m3"]
    assert "concrete_unit_weight_kn_m3" in prepare(r).missing_parameters
    with pytest.raises(ValueError):
        confirm(prepare(r))


def test_complete_evaluation_records_failed_reason():
    s = run(request("existing_beam"))
    assert "抗弯承载力低于设计弯矩" in result(s, "flexural_check")["reasons"]


@pytest.mark.parametrize("failure", ["network", "format", "tool"])
def test_model_failure_cannot_form_pass(failure):
    r = request()
    class BadRoles(FixtureRoles):
        def plan(self, role, payload):
            if failure == "network":
                raise TimeoutError("private key must never be echoed")
            if failure == "format":
                return {"wrong": 3}
            return RolePlan(steps=["execute_arbitrary_code"], explanation="bad")
    s = run_engineering(confirm(prepare(r)), BadRoles(r))
    assert s.evaluation.status == "error" and not s.tool_results
    assert "private key" not in markdown_report(s)


def test_evaluation_model_failure_after_design_cannot_pass():
    r = request()
    class BadEvaluation(FixtureRoles):
        def plan(self, role, payload):
            if role == "Evaluation":
                raise TimeoutError()
            return super().plan(role, payload)
    s = run_engineering(confirm(prepare(r)), BadEvaluation(r))
    assert s.candidate and s.evaluation.status == "error"


def test_unsupported_has_no_calculations():
    r = TaskRequest(task_type="unsupported", user_query="悬臂框架")
    s = run_engineering(prepare(r), FixtureRoles(r))
    assert s.evaluation.status == "incomplete" and not s.tool_results


def test_reports_preserve_trace_and_do_not_overwrite(tmp_path):
    s = run(request())
    md, data = save_reports(s, tmp_path)
    md2, _ = save_reports(s, tmp_path)
    assert md != md2 and md.exists()
    restored = json.loads(data.read_text(encoding="utf-8"))
    assert restored["evaluation"]["overall_status"] == "incomplete"
    text = md.read_text(encoding="utf-8")
    assert "长期挠度" in text and "未完成" in text and "输入哈希" in text


def test_cli_confirmation_edits_and_missing_field_recovery():
    from engi_agent.engineering.cli import interactive_confirm
    r = request()
    del r.parameters["live_load_kn_m"]
    answers = iter(["确认", 'live_load_kn_m={"value":1,"unit":"kip/ft"}', "确认"])
    s = interactive_confirm(r, input_fn=lambda _: next(answers), output_fn=lambda _: None)
    assert s.confirmed
    assert s.request.parameters["live_load_kn_m"].source == "user"


def test_cli_cancel_does_not_run():
    from engi_agent.engineering.cli import interactive_confirm
    assert interactive_confirm(request(), input_fn=lambda _: "quit", output_fn=lambda _: None) is None
