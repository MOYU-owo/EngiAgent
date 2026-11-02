"""Three bounded live turns: quantities, a concept, and its contextual follow-up."""
import json
from pathlib import Path
from langchain_deepseek import ChatDeepSeek
from engi_agent.config import Settings
from engi_agent.engineering.consultation import DeepSeekConsultant
from engi_agent.ui.service import WorkbenchSession,load_case


def main():
    settings=Settings.from_env()
    model=ChatDeepSeek(model=settings.model,api_key=settings.deepseek_api_key,temperature=0,max_retries=0,timeout=45)
    client=DeepSeekConsultant(model)
    session=WorkbenchSession();session.load(load_case('完整新方案设计'),'对话验收');session.confirm();session.run('program')
    before=session.result.model_dump_json()
    for question in ('当前参数是多少，用钢量多少？','什么是准永久组合？请用通俗的话解释。','那它为什么会影响裂缝？'):
        reply=session.ask_expert(question,'DeepSeek',client)
        assert reply.decision.intent=='explain' and reply.answer_source=='model' and len(reply.answer)>60
        assert not reply.preview and session.result.model_dump_json()==before
        print(json.dumps({'query':question,'answer':reply.answer},ensure_ascii=False),flush=True)
    directory=Path('outputs/expert_dialogue');directory.mkdir(parents=True,exist_ok=True)
    (directory/'live_audit.json').write_bytes(session.downloads()['audit'])
    print('Three live dialogue turns passed; engineering state unchanged.',flush=True)


if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('Live dialogue check failed: '+type(exc).__name__)
        raise SystemExit(1)
