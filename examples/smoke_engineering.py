"""Small paid DeepSeek integration check; separate from offline pytest.

The live extracted values must match the reviewed fixture before this script
explicitly confirms them. It never confirms unknown or changed model values.
"""
import json
import math
from pathlib import Path
from engi_agent.engineering.roles import DeepSeekRoles
from engi_agent.engineering.schema import TaskRequest
from engi_agent.engineering.workflow import prepare, confirm, run_engineering
from engi_agent.engineering.reporting import save_reports

QUERY = """请新设计一根单跨简支、矩形截面、单层受拉纵筋的钢筋混凝土梁。
全跨均布恒载0.82 kip/ft（不含梁自重，计算时请计入），全跨均布活载1 kip/ft。
跨度25 ft，宽12 in，高20 in；混凝土圆柱抗压强度4.35 ksi，容重150 lb/ft3。
纵筋屈服强度60 ksi，单根直径1.128 in，公称面积1 in2。
箍筋屈服强度60 ksi，直径0.375 in，单肢公称面积0.11 in2，双肢。
净保护层1.5 in，最大骨料0.75 in。混凝土弹性模量27568.7 MPa。
请做抗弯、抗剪和毛截面弹性挠度教学试算；挠度教学限值L/240。
只按这些明确输入提取参数，不补充其他工程条件。
"""


def main():
    roles = DeepSeekRoles()
    expected = prepare(TaskRequest.model_validate_json(
        Path("examples/engineering/paper_normal.json").read_text(encoding="utf-8")))
    extracted = prepare(roles.parse(QUERY))
    assert extracted.request.task_type == "new_design"
    assert not extracted.missing_parameters, extracted.missing_parameters
    assert set(extracted.request.parameters) == set(expected.request.parameters), "模型提取字段与参考不一致，未确认"
    for key, actual in extracted.request.parameters.items():
        want = expected.request.parameters[key].value
        if isinstance(want, float):
            assert math.isclose(float(actual.value), want, rel_tol=1e-6, abs_tol=1e-6), key
        else:
            assert actual.value == want, key
    state = confirm(extracted)
    state.role_events.append({"role": "Dispatcher", "status": "success", "mode": "DeepSeek"})
    state = run_engineering(state, roles)
    save_reports(state, "outputs/live")
    assert state.evaluation.status == "pass", state.errors
    assert state.candidate["bar_count"] == 4
    print(json.dumps({"case": "live_design", "status": state.evaluation.status,
                      "roles": state.role_events, "candidate": state.candidate}, ensure_ascii=False))
    # Independent existing-beam entry; no Design invocation.
    r = TaskRequest.model_validate_json(Path("examples/engineering/flexure_only.json").read_text(encoding="utf-8"))
    existing = run_engineering(confirm(prepare(r)), roles)
    save_reports(existing, "outputs/live")
    assert existing.evaluation.status == "fail", existing.errors
    assert [e["role"] for e in existing.role_events] == ["Evaluation"]
    print(json.dumps({"case": "live_existing_flexure", "status": existing.evaluation.status,
                      "checks": existing.evaluation.checks}, ensure_ascii=False))


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        main()
    except Exception as exc:
        print(f"Live smoke failed: {type(exc).__name__}")
        raise SystemExit(1)
