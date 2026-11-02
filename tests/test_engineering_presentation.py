"""Engineer-facing contracts: truthful progress, readable tables and precision."""
import json
from pathlib import Path
import pytest
from engi_agent.engineering.cli import confirmation_text, edit_parameter, interactive_confirm, main
from engi_agent.engineering.cn_presentation import parameter_keys, parameter_rows, progress_text, number
from engi_agent.engineering.cn_presentation import markdown_report, save_reports
from engi_agent.engineering.roles import FixtureRoles
from engi_agent.engineering.cn_schema import TaskRequest, ParameterValue, EngineeringState
from engi_agent.engineering.cn_workflow import prepare, confirm, run_engineering
from engi_agent.engineering.cn_tools import REGISTRY
from engi_agent.engineering.cn_presentation import overview as result_overview

ROOT = Path(__file__).resolve().parents[1]


def request(name="cn_design"):
    return TaskRequest.model_validate_json((ROOT / "examples/engineering" / (name + ".json")).read_text(encoding="utf-8"))


def run(r, observer=None):
    return run_engineering(confirm(prepare(r)), FixtureRoles(r), on_event=observer)


def test_confirmation_translates_labels_enum_sources_and_retains_original_precision():
    state = prepare(request())
    text = confirmation_text(state)
    assert all(word in text for word in ("参数", "来源", "待确认", "跨度", "简支", "全跨均布"))
    assert "span_mm" not in text and '"gamma_dead"' not in text
    rows = parameter_rows(state)
    assert any(row[2] == "纵筋直径" and row[3] == "20 mm" for row in rows)
    assert any(row[2] == "纵筋根数" and row[4] == "由设计工具确定" for row in rows)
    assert any(row[2] == "自重约定" and "另行计入" in row[4] for row in rows)


def test_missing_required_and_computed_fields_are_distinct():
    r = request()
    del r.parameters["beam_depth_mm"]
    del r.parameters["live_load_kn_m"]
    rows = parameter_rows(prepare(r))
    assert any(row[2] == "活载" and row[-1] == "缺失" for row in rows)
    assert any(row[2] == "梁高" and row[-1] == "待计算" for row in rows)


def test_completed_generated_parameters_show_calculated_in_report():
    state = run(request())
    rows = parameter_rows(state)
    assert any(row[2] == "纵筋根数" and row[4] == "3" and row[-1] == "已计算" for row in rows)
    assert any(row[2] == "箍筋间距" and row[4] == "350 mm" and row[-1] == "已计算" for row in rows)


def test_display_rounding_removes_binary_tail_but_preserves_small_strains():
    assert number(112.27499999999999) == "112.28"
    assert number(0.003) == "0.003"
    assert number(6000) == "6,000"


def test_chinese_and_numbered_edits_preserve_units_and_require_reconfirmation():
    r = request()
    r = edit_parameter(r, "修改 跨度 6 m")
    assert prepare(r).request.parameters["span_mm"].value == 6000
    index = parameter_keys(prepare(r)).index("span_mm") + 1
    r = edit_parameter(r, f"修改 {index} 6500 mm", prepare(r))
    item = prepare(r).request.parameters["span_mm"]
    assert item.value == 6500 and not item.confirmed and item.source == "user"
    r = edit_parameter(r, "修改 自重约定 已含自重")
    assert prepare(r).request.parameters["self_weight_mode"].value == "included"


@pytest.mark.parametrize("text", ["修改 跨度 6", "修改 纵筋根数 2.5", "修改 跨度 -6 m", "修改 不存在 3 mm"])
def test_invalid_edits_are_rejected(text):
    with pytest.raises(ValueError):
        edit_parameter(request(), text)


def test_interactive_missing_field_can_be_filled_in_chinese():
    r = request()
    del r.parameters["live_load_kn_m"]
    messages = []
    answers = iter(["确认", "修改 活载 5 kN/m", "确认"])
    state = interactive_confirm(r, input_fn=lambda _: next(answers), output_fn=messages.append)
    assert state.confirmed and state.request.parameters["live_load_kn_m"].value == 5
    assert any("缺失" in message for message in messages)


def test_progress_uses_actual_executed_tool_outputs(monkeypatch):
    seen = []
    original = REGISTRY["beam_analysis"]
    def checked(*args):
        assert sum(e.name == "beam_analysis" and e.kind == "tool" for e in seen) == len([e for e in seen if e.name == "Evaluation" and e.status == "running"])
        return original(*args)
    monkeypatch.setitem(REGISTRY, "beam_analysis", checked)
    state = run(request(), seen.append)
    assert state.evaluation.status == "pass"
    assert len(seen) == len(state.progress_events)
    tool_events = [e for e in seen if e.kind == "tool"]
    assert [e.step for e in tool_events if e.phase == "design" and e.status == "success"] == list(range(1, 9))
    for event in tool_events:
        if event.status == "success":
            result = state.tool_results[f"{event.phase}.{event.name}"]
            assert event.outputs == result.outputs
    assert "[设计 1/8]" in progress_text(tool_events[0])


def test_observer_cannot_mutate_result_and_display_failure_does_not_change_engineering():
    def mutating(event):
        event.outputs["pass"] = False
        raise RuntimeError("display failure")
    state = run(request(), mutating)
    assert state.evaluation.status == "pass"
    assert len(state.presentation_warnings) == 1
    assert state.tool_results["evaluation.flexural_check"].outputs["pass"] is True
    assert "pass" not in state.progress_events[0].outputs


def test_failed_check_is_not_displayed_as_execution_failure_or_overall_pass():
    seen = []
    r = request("cn_flexure_only")
    r.parameters["design_moment_kn_m"] = ParameterValue(value=200, unit="kN·m")
    state = run(r, seen.append)
    event = next(e for e in seen if e.name == "flexural_check" and e.status == "success")
    assert "不通过" in progress_text(event)
    assert "抗弯承载力" in progress_text(event)
    overview = result_overview(state)
    assert "请求项目不通过" in overview and "抗弯：不通过" in overview
    assert all(e.phase == "evaluation" for e in seen)


def test_blocked_descendants_are_recorded_and_not_claimed_to_pass():
    r = request(); r.parameters["max_depth_mm"] = ParameterValue(value=400, unit="mm")
    state = run(r)
    assert any(e.status == "blocked" for e in state.progress_events)
    text = markdown_report(state)
    assert "上游阻断" in text and "请求项目通过" not in text


def test_model_failure_shows_planning_failure_without_fake_tool_progress():
    class Broken(FixtureRoles):
        def plan(self, *args):
            raise TimeoutError()
    r = request()
    seen = []
    state = run_engineering(confirm(prepare(r)), Broken(r), on_event=seen.append)
    assert state.evaluation.status == "error"
    assert [e.status for e in seen] == ["running", "failed"]
    assert not any(e.kind == "tool" for e in seen)
    assert "不能判定通过" in markdown_report(state)


def test_report_is_engineering_tables_not_json_dump_and_json_keeps_full_precision(tmp_path):
    state = run(request())
    md, data = save_reports(state, tmp_path)
    text = md.read_text(encoding="utf-8")
    assert "参数确认" in text and "分项计算过程" in text and "独立验算" in text
    assert "| 检查项目 | 结果 | 关键数值 |" in text
    assert "```json" not in text
    assert data.name in text and "输入哈希" in text
    saved = json.loads(data.read_text(encoding="utf-8"))
    assert saved["candidate"]["As_mm2"] == state.candidate["As_mm2"]
    assert saved["progress_events"] and saved["evaluation"]["overall_status"] == "incomplete"
    assert "156.9074" in text and str(state.tool_results["evaluation.flexural_check"].outputs["capacity_kn_m"]) not in text


def test_existing_evaluation_report_displays_actual_scheme_instead_of_empty_candidate():
    text = markdown_report(run(request("cn_flexure_only")))
    assert "已有梁独立验算" in text
    assert "纵筋根数" in text and "设计 · 受弯配筋" not in text
    assert "本次未请求：抗剪" in text


def test_old_saved_states_without_progress_remain_readable():
    old = run(request()).model_dump()
    old.pop("progress_events")
    old.pop("presentation_warnings")
    state = EngineeringState.model_validate_json(json.dumps(old))
    assert not state.progress_events
    assert "156.9074" in markdown_report(state)


def test_cli_uses_readable_progress_and_short_result_summary(tmp_path, capsys):
    code = main(["--request", str(ROOT / "examples/engineering/cn_design.json"),
                 "--offline", "--approve", "--output-dir", str(tmp_path)])
    text = capsys.readouterr().out
    assert code == 0 and "[设计 1/8]" in text and "[独立验算 11/11]" in text
    assert "计算状态：请求项目通过" in text and "参数确认" in text
    assert "```json" not in text and "输入哈希" not in text
