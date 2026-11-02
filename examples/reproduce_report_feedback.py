"""Rebuild the supplied report's explicit parameters; preserve the original file.

This recreates engineering inputs, not the original hosted-model invocation/audit.
"""
import json
from pathlib import Path
from engi_agent.engineering.cn_schema import TaskRequest, ParameterValue
from engi_agent.engineering.cn_workflow import prepare, confirm, run_engineering
from engi_agent.engineering.roles import ProgramRoles
from engi_agent.engineering.cn_presentation import markdown_report


def report_request():
    r=TaskRequest.model_validate_json(Path('examples/engineering/cn_design.json').read_text(encoding='utf-8'))
    for k,v,u in [('concrete_grade','C50',None),('steel_grade','HRB500',None),('stirrup_grade','HPB300',None),
                  ('dead_load_kn_m',20,'kN/m'),('cover_mm',35,'mm'),('support_width_mm',1200,'mm')]:
        r.parameters[k]=ParameterValue(value=v,unit=u)
    r.user_query='按用户提供计算书参数重建：跨度6m，300×550mm，C50，HRB500，HPB300，保护层35mm，恒载20kN/m不含自重，活载5kN/m，支座宽1200mm；其余条件见确认表。'
    return r


def main():
    directory=Path('outputs/feedback_report');directory.mkdir(parents=True,exist_ok=True)
    baseline=report_request();baseline.auto_redesign=False
    optimized=report_request();optimized.auto_redesign=True
    optimized.solution_count=2;optimized.search_diameters_mm=[20,22];optimized.max_iterations=6
    records=[]
    for name,r in [('原案例_补充计算书',baseline),('改设后_候选比较计算书',optimized)]:
        state=run_engineering(confirm(prepare(r)),ProgramRoles())
        (directory/(name+'.json')).write_text(state.model_dump_json(indent=2),encoding='utf-8')
        (directory/(name+'.md')).write_text(markdown_report(state,name+'.json'),encoding='utf-8')
        records.append({'case':name,'status':state.evaluation.status,'candidate':state.candidate,
            'crack_mm':state.tool_results['evaluation.crack_check'].outputs['crack_width_mm'],
            'deflection_mm':state.tool_results['evaluation.deflection_check'].outputs['deflection_mm'],
            'alternatives':state.design_alternatives,'iterations':len(state.revisions)})
    (directory/'summary.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(records,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
