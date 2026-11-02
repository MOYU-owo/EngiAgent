"""Three bounded live consultation requests, with exact checks before demo confirmation."""
import json
from pathlib import Path
from langchain_deepseek import ChatDeepSeek
from engi_agent.config import Settings
from engi_agent.engineering.consultation import DeepSeekConsultant
from engi_agent.engineering.cn_workflow import prepare,confirm,run_engineering
from engi_agent.engineering.roles import ProgramRoles
from engi_agent.ui.service import WorkbenchSession,load_case


def main():
    settings=Settings.from_env()
    client=DeepSeekConsultant(ChatDeepSeek(model=settings.model,api_key=settings.deepseek_api_key,
                                        temperature=0,max_retries=0,timeout=30))
    session=WorkbenchSession();session.load(load_case('已有梁独立验算'),'受控真实咨询测试')
    session.confirm();session.run('program')
    explanation=session.ask_expert('为什么抗弯通过仍需要检查长期挠度？','DeepSeek',client)
    assert explanation.decision.intent=='explain' and 'deflection' in explanation.decision.focus
    delta=session.ask_expert('梁高改为0.6m，活载改为6kN/m，其余参数和原验算项目保持。','DeepSeek',client)
    assert delta.decision.intent=='modify'
    assert set(delta.decision.changes)=={'beam_depth_mm','live_load_kn_m'}
    assert {r['field']:r['采用值'] for r in delta.preview}=={'beam_depth_mm':600,'live_load_kn_m':6}
    clarification=session.ask_expert('活载提高一点，其他不要改。','DeepSeek',client)
    assert clarification.decision.intent=='clarify'
    # Confirm only these exact known test inputs, never arbitrary provider proposals.
    session.adopt_expert_proposal(delta.id);session.confirm();session.run('program')
    full=run_engineering(confirm(prepare(session.result.request)),ProgramRoles())
    assert {k:v.outputs for k,v in full.tool_results.items()}=={k:v.outputs for k,v in session.result.tool_results.items()}
    folder=Path('outputs/research');folder.mkdir(parents=True,exist_ok=True)
    (folder/'consultation_live_audit.json').write_bytes(session.downloads()['audit'])
    (folder/'consultation_live_result.json').write_bytes(session.downloads()['json'])
    print(json.dumps({'live_calls':3,'status':session.result.evaluation.status,
                      'partial_equals_full':True,'audit':str(folder/'consultation_live_audit.json')},ensure_ascii=True))


if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('Live consultation validation failed: '+type(exc).__name__)
        raise SystemExit(1)
