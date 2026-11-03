"""Recreate the confirmed unsized inputs in the 2026-11-03 user report.

The report's original prose still says fixed 300x550; its confirmed table and
tool inputs omit both dimensions. This fixture follows the latter, explicitly.
"""
import json
from pathlib import Path
from reproduce_report_feedback import report_request
from engi_agent.engineering.cn_workflow import prepare, confirm, run_engineering
from engi_agent.engineering.roles import ProgramRoles
from engi_agent.engineering.cn_presentation import markdown_report


def unsized_request(iterations=12):
    r = report_request()
    for k in ('beam_width_mm', 'beam_depth_mm'):
        r.parameters.pop(k)
    r.auto_redesign = True
    r.max_iterations = iterations
    r.search_diameters_mm = [20, 22]
    r.solution_count = 3
    r.user_query = '按计算书确认表重建：梁宽、梁高留空，由程序设计；其他条件见参数确认表。允许20/22mm纵筋，最多展示3个通过初筛的方案。'
    return r


def reported_final_request():
    from engi_agent.engineering.cn_schema import ParameterValue
    r = unsized_request()
    r.task_type = 'evaluate_existing'; r.auto_redesign = False
    for k, v in dict(beam_width_mm=250, beam_depth_mm=500, bar_diameter_mm=22,
                     bar_count=6, stirrup_spacing_mm=300).items():
        r.parameters[k] = ParameterValue(value=v,unit='mm' if k.endswith('_mm') else None)
    r.user_query = '独立复核用户计算书末轮的实际方案：250×500mm，6Φ22，双肢Φ8@300；其余条件取确认表。'
    return r


def main():
    directory = Path('outputs/section_feedback')
    directory.mkdir(parents=True, exist_ok=True)
    summary = []
    for name, request in [('原计算书末轮_独立复核',reported_final_request()),
                          ('原轮次预算_6轮',unsized_request(6)), ('截面配筋搜索_12轮',unsized_request(12))]:
        state = run_engineering(confirm(prepare(request)), ProgramRoles())
        (directory/(name+'.json')).write_text(state.model_dump_json(indent=2), encoding='utf-8')
        (directory/(name+'.md')).write_text(markdown_report(state, name+'.json'), encoding='utf-8')
        summary.append(dict(case=name, status=state.evaluation.status, candidate=state.candidate,
                            search=state.design_search, alternatives=state.design_alternatives,
                            stop=state.search_stop_reason))
    (directory/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
