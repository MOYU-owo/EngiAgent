"""Direct answers, actual-scheme quantities, history, references and math rendering."""
import json
import pytest
from engi_agent.engineering.consultation import DeepSeekConsultant, ConsultationDecision, context
from engi_agent.ui.service import WorkbenchSession,load_case
from engi_agent.engineering.references import professional_references
from engi_agent.ui.latex_steps import numeric_latex,step_formula


def session():
    s=WorkbenchSession();s.load(load_case('完整新方案设计'),'dialogue');s.confirm();s.run('program');return s


def test_offline_parameter_quantity_question_does_not_fall_back_to_unrelated_scope():
    s=session();reply=s.ask_expert('当前参数是多少，用钢量多少')
    assert '3' in reply.answer and 'Φ20' in reply.answer and 'mm²' in reply.answer
    assert 'kg' in reply.answer and '不含' in reply.answer and '全梁总用钢量' in reply.answer
    assert {e.title for e in reply.evidence}=={'当前参数','用钢量统计范围'}


def test_model_answers_are_used_and_previous_answer_is_sent_as_assistant_message():
    class Model:
        calls=[]
        def with_structured_output(self,schema,method):
            assert schema is ConsultationDecision
            return self
        def invoke(self,messages):
            self.calls.append(messages)
            payload=json.loads(messages[-1].content)
            q=payload['current']['actual_scheme_and_quantity']
            assert q['actual_parameters']['bar_count']==3
            assert q['bottom_kg_per_m']==pytest.approx(q['bottom_area_mm2']*.00785)
            if len(self.calls)>1:
                assert any(m.type=='ai' and '准永久组合' in m.content for m in messages)
            return {'intent':'explain','focus':['general'],'answer':'准永久组合反映长期持续作用，活载按准永久系数折减；这与结构长期变形和裂缝有关。'}
    s=session();model=Model();client=DeepSeekConsultant(model)
    before=s.result.model_dump_json()
    first=s.ask_expert('什么是准永久组合','DeepSeek',client)
    assert first.answer.startswith('准永久组合') and first.answer_source=='model' and not first.evidence
    s.ask_expert('为什么影响裂缝','DeepSeek',client)
    assert s.result.model_dump_json()==before and len(model.calls)==2
    assert json.loads(s.downloads()['audit'])['consultations'][0]['answer']==first.answer


def test_quantity_uses_actual_selected_reinforcement_not_initial_diameter():
    s=session();s.result.candidate.update(bar_count=3,bar_diameter_mm=22)
    # The area remains the actual recorded area; never synthesize capacities from a UI selection.
    data=context(s.result)['actual_scheme_and_quantity']
    assert data['actual_parameters']['bar_diameter_mm']==22
    assert data['bottom_area_mm2']==s.result.tool_results['evaluation.flexural_check'].outputs['As_mm2']


def test_only_formal_references_are_presented():
    refs=professional_references(['GB/T50010 6.2.1、6.2.6—6.2.10','GB55008 4.4.6',
        'docs/rc_beam_cn_design_spec.md','结构力学：简支梁','项目经验L/12','arbitrary standard'])
    assert len(refs)==2 and '混凝土结构设计标准' in refs[0] and '2024年版' in refs[0]
    assert all('docs/' not in x and '项目经验' not in x for x in refs)


def test_numeric_substitution_is_latex_and_never_executed():
    assert r'\frac' in numeric_latex('119.8125×10⁶/(0.87×497×942.4778)')
    assert r'\pi' in numeric_latex('3×π×20²/4')
    assert numeric_latex("__import__('os').system('echo unsafe')") is None
    assert numeric_latex('V=10；s=20') is None
    assert step_formula({'title':'裂缝宽度'}).startswith('w_')
