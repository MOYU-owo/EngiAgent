"""Small live DeepSeek check. Only known example values may be auto-confirmed."""
import json
import math
from pathlib import Path
from engi_agent.engineering.roles import DeepSeekRoles
from engi_agent.engineering.schema import TaskRequest
from engi_agent.engineering.workflow import prepare,confirm,run_engineering
from engi_agent.engineering.reporting import save_reports

QUERY='''按中国规范cn-2024新设计一根普通房屋钢筋混凝土梁：单跨理想简支、矩形、单层受拉纵筋、全跨均布恒活载。
计算跨度6m，梁宽300mm，梁高550mm，支座宽1000mm。净保护层30mm，最大骨料20mm。
混凝土C30，容重25kN/m3；纵筋HRB400直径20mm；箍筋HRB400直径8mm、双肢，间距由程序设计。
恒载10kN/m不含梁自重，请另计；活载5kN/m。活载组合值系数0.7、频遇值系数0.6、准永久值系数0.5。
设计工作年限50年、安全等级二级、重要性系数1.0、一类环境。
裂缝限值0.3mm，挠度限值L/250。端部充分受拉直锚800mm，锚固区箍筋间距100mm。
上部架立筋2根直径12mm；每侧腰筋2根直径12mm，腰筋间距180mm。
进行抗弯、抗剪、构造、裂缝和长期挠度检查，本次关闭自动改设。'''


def main():
    roles=DeepSeekRoles()
    expected=prepare(TaskRequest.model_validate_json(Path('examples/engineering/cn_design.json').read_text(encoding='utf-8')))
    print('开始Dispatcher参数提取。',flush=True)
    parsed=roles.parse(QUERY)
    Path('outputs/cn_live').mkdir(parents=True,exist_ok=True)
    Path('outputs/cn_live/extracted_request.json').write_text(parsed.model_dump_json(indent=2),encoding='utf-8')
    print('参数提取完成，开始类型/单位校验。',flush=True)
    extracted=prepare(parsed)
    if extracted.request.code!='cn-2024' or extracted.request.task_type!='new_design':
        raise ValueError('模型任务体系不匹配，未确认')
    if set(extracted.request.parameters)!=set(expected.request.parameters):
        print(json.dumps({'missing':sorted(set(expected.request.parameters)-set(extracted.request.parameters)),
                          'extra':sorted(set(extracted.request.parameters)-set(expected.request.parameters))},ensure_ascii=False))
        raise ValueError('模型提取字段不匹配，未确认')
    for key,actual in extracted.request.parameters.items():
        want=expected.request.parameters[key].value
        if isinstance(want,float):
            if not math.isclose(float(actual.value),want,rel_tol=1e-8,abs_tol=1e-8): raise ValueError('模型值不匹配：'+key)
        elif actual.value!=want: raise ValueError('模型值不匹配：'+key)
    print('Dispatcher完整参数匹配，确认受控参考案例。',flush=True)
    state=run_engineering(confirm(extracted),roles)
    md,data=save_reports(state,'outputs/cn_live')
    assert state.evaluation.status=='pass',state.errors
    print(json.dumps({'case':'live_cn_natural_design','status':state.evaluation.status,
                      'candidate':state.candidate,'reports':[str(md),str(data)]},ensure_ascii=False),flush=True)
    # One additional hosted Evaluation call, no repeated parser call.
    r=TaskRequest.model_validate_json(Path('examples/engineering/cn_flexure_only.json').read_text(encoding='utf-8'))
    s=run_engineering(confirm(prepare(r)),roles)
    assert s.evaluation.status=='pass'
    md,data=save_reports(s,'outputs/cn_live')
    print(json.dumps({'case':'live_cn_flexure','status':s.evaluation.status,'report':str(md)},ensure_ascii=False),flush=True)


if __name__=='__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    try: main()
    except Exception as exc:
        print('真实模型验证未通过：'+type(exc).__name__)
        from pydantic import ValidationError
        if isinstance(exc,ValidationError):
            print(json.dumps([{'loc':e['loc'],'type':e['type']} for e in exc.errors()],ensure_ascii=False))
        raise SystemExit(1)
