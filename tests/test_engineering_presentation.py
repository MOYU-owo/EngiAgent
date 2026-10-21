"""Engineer-facing contracts: truthful progress, readable tables and precision."""
import json
from pathlib import Path
import pytest
from engi_agent.engineering.cli import confirmation_text, edit_parameter, interactive_confirm, main
from engi_agent.engineering.presentation import parameter_keys, parameter_rows, progress_text, result_overview, number
from engi_agent.engineering.reporting import markdown_report, save_reports
from engi_agent.engineering.roles import FixtureRoles
from engi_agent.engineering.schema import TaskRequest, ParameterValue, EngineeringState
from engi_agent.engineering.workflow import prepare, confirm, run_engineering
from engi_agent.engineering.tools import REGISTRY

ROOT = Path(__file__).resolve().parents[1]


def request(name="paper_normal"):
    return TaskRequest.model_validate_json((ROOT / "examples/engineering" / (name + ".json")).read_text(encoding="utf-8"))


def run(r, observer=None):
    return run_engineering(confirm(prepare(r)), FixtureRoles(r), on_event=observer)


def test_confirmation_translates_labels_enum_sources_and_retains_original_precision():
    state = prepare(request())
    text = confirmation_text(state)
    assert all(word in text for word in ("参数", "来源", "待确认", "跨度", "简支", "全跨均布"))
    assert "span_mm" not in text and '"gamma_dead"' not in text
    rows = parameter_rows(state)
    assert any(row[2] == "纵筋直径" and row[3] == "1.128 in" for row in rows)
    assert any(row[2] == "纵筋根数" and row[4] == "由设计工具确定" for row in rows)
    assert any(row[2] == "自重约定" and "另行计入" in row[4] for row in rows)


def test_missing_required_and_computed_fields_are_distinct():
    r = request("unsized_design")
    del r.parameters["live_load_kn_m"]
    rows = parameter_rows(prepare(r))
    assert any(row[2] == "活载" and row[-1] == "缺失" for row in rows)
    assert any(row[2] == "梁高" and row[-1] == "待计算" for row in rows)


def test_completed_generated_parameters_show_calculated_in_report():
    state = run(request())
    rows = parameter_rows(state)
    assert any(row[2] == "纵筋根数" and row[4] == "4" and row[-1] == "已计算" for row in rows)
    assert any(row[2] == "箍筋间距" and row[4] == "220 mm" and row[-1] == "已计算" for row in rows)


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


def test_progress_is_delivered_before_tool_execution_and_uses_real_results(monkeypatch):
    seen = []
    original = REGISTRY["beam_analysis"]
    def checked(*args):
        assert seen[-1].name == "beam_analysis" and seen[-1].status == "running"
        return original(*args)
    monkeypatch.setitem(REGISTRY, "beam_analysis", checked)
    state = run(request(), seen.append)
    assert state.evaluation.status == "pass"
    assert len(seen) == len(state.progress_events)
    tool_events = [e for e in seen if e.kind == "tool"]
    assert [e.step for e in tool_events if e.phase == "design" and e.status == "success"] == list(range(1, 7))
    for event in tool_events:
        if event.status == "success":
            result = state.tool_results[f"{event.phase}.{event.name}"]
            assert event.outputs == result.outputs
    assert "[设计 1/6]" in progress_text(tool_events[0])


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
    state = run(request("flexure_only"), seen.append)
    event = next(e for e in seen if e.name == "flexural_check" and e.status == "success")
    assert "不通过" in progress_text(event)
    assert "折减后抗弯承载力" in progress_text(event)
    overview = result_overview(state)
    assert "试算不通过" in overview and "抗弯承载力低于设计弯矩" in overview
    assert all(e.phase == "evaluation" for e in seen)


def test_blocked_descendants_and_absent_checks_are_not_claimed_to_pass():
    state = run(request("unsized_design"))
    assert any(e.status == "blocked" for e in state.progress_events)
    text = markdown_report(state)
    assert "未形成有效设计方案" in text and "上游阻断" in text
    assert "未执行或被上游阻断；不能判断通过" in text


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
    assert "不能判断通过" in markdown_report(state)


def test_report_is_engineering_tables_not_json_dump_and_json_keeps_full_precision(tmp_path):
    state = run(request())
    md, data = save_reports(state, tmp_path)
    text = md.read_text(encoding="utf-8")
    assert "参数确认表" in text and "设计计算过程" in text and "独立验算过程" in text
    assert "| 验算项目 | 需求/限值 | 能力/计算响应 | 结论 |" in text
    assert "```json" not in text
    assert data.name in text and "输入哈希" in text
    saved = json.loads(data.read_text(encoding="utf-8"))
    assert saved["candidate"]["As_mm2"] == state.candidate["As_mm2"]
    assert saved["progress_events"] and saved["evaluation"]["overall_status"] == "incomplete"
    assert "305.48" in text and "305.482731483362" not in text


def test_existing_evaluation_report_displays_actual_scheme_instead_of_empty_candidate():
    text = markdown_report(run(request("flexure_only")))
    assert "已有方案" in text and "没有生成新设计方案" in text
    assert "纵筋根数" in text and "跳过设计阶段" in text
    assert "本次未请求：抗剪" in text


def test_old_saved_states_without_progress_remain_readable():
    old = run(request()).model_dump()
    old.pop("progress_events")
    old.pop("presentation_warnings")
    state = EngineeringState.model_validate_json(json.dumps(old))
    assert not state.progress_events
    assert "362.57" in markdown_report(state)


def test_cli_uses_readable_progress_and_short_result_summary(tmp_path, capsys):
    code = main(["--engineering", "--request", str(ROOT / "examples/engineering/paper_normal.json"),
                 "--offline", "--approve", "--output-dir", str(tmp_path)])
    text = capsys.readouterr().out
    assert code == 0 and "[设计 1/6]" in text and "[验算 8/8]" in text
    assert "结果总览" in text and "参数确认" in text
    assert "```json" not in text and "输入哈希" not in text
