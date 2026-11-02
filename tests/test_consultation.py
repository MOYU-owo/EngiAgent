"""Grounding, state transitions and stale-proposal protection with real beam tools."""
import json
import pytest

from engi_agent.engineering.consultation import (
    consult, apply_proposal, basis_hash, ConsultationDecision, DeepSeekConsultant)
from engi_agent.engineering.cn_workflow import prepare, confirm, run_engineering
from engi_agent.engineering.roles import FixtureRoles
from engi_agent.ui.service import WorkbenchSession, load_case


def session(case='已有梁独立验算'):
    s=WorkbenchSession();s.load(load_case(case),case);s.confirm();s.run('offline')
    return s


class DecisionClient:
    def __init__(self, decision): self.decision=decision
    def consult(self, query, evidence, history): return ConsultationDecision.model_validate(self.decision)


def test_explanation_cites_actual_failed_tool_without_mutating_state():
    s=session('改设达到上限停止');before=basis_hash(s.result)
    reply=s.ask_expert('裂缝为什么不通过？')
    item=reply.evidence[0]
    assert item.outputs==s.result.tool_results['evaluation.crack_check'].outputs
    assert item.outputs['pass'] is False and item.references
    assert '最大裂缝宽度超限' in item.text
    assert basis_hash(s.result)==before and s.completed_runs==1
    assert s.calls[-1].role=='ExpertConsultation' and s.calls[-1].mode=='offline'


def test_adopt_height_delta_requires_confirmation_and_matches_full_recompute():
    s=session();reply=s.ask_expert('梁高改为0.6m')
    assert reply.preview[0]['采用值']==600
    old=basis_hash(s.result)
    pending=s.adopt_expert_proposal(reply.id)
    assert s.stage=='validated' and not pending.confirmed
    assert basis_hash(s.result)==old
    with pytest.raises(ValueError):s.run('offline')
    s.confirm();s.run('offline')
    full=run_engineering(confirm(prepare(s.result.request)),FixtureRoles(s.result.request))
    assert {k:v.outputs for k,v in s.result.tool_results.items()}=={k:v.outputs for k,v in full.tool_results.items()}
    assert any(t['action']=='reuse' for t in s.result.plan_trace)
    with pytest.raises(ValueError):s.adopt_expert_proposal(reply.id)


def test_new_design_modification_preserves_actual_designed_reinforcement():
    s=session('挠度超限后有限改设');assert s.result.candidate['bar_count']==4
    reply=s.ask_expert('活载改为6kN/m')
    pending=s.adopt_expert_proposal(reply.id)
    assert pending.request.task_type=='evaluate_existing'
    assert int(pending.request.parameters['bar_count'].value)==4
    assert pending.request.parameters['stirrup_spacing_mm'].value==350
    assert not pending.request.auto_redesign
    assert pending.request.targets==s.result.request.targets


@pytest.mark.parametrize('query',[
    '梁高改为600mm，梁高改为650mm','活载增加2kN/m',
    '梁高改为600mm，活载提高一点','梁高不要改为600mm',
])
def test_ambiguous_relative_or_negated_delta_does_not_get_applied(query):
    s=session();r=s.ask_expert(query)
    assert r.decision.intent=='clarify' and not r.preview
    with pytest.raises(ValueError):s.adopt_expert_proposal(r.id)


@pytest.mark.parametrize('query,change',[
    ('梁高改为600mm',{'beam_depth_mm':{'value':650,'unit':'mm','quote':'梁高改为600mm'}}),
    ('梁高改为600mm',{'span_mm':{'value':600,'unit':'mm','quote':'梁高改为600mm'}}),
    ('梁高改为600mm',{'beam_depth_mm':{'value':600,'unit':'m','quote':'梁高改为600mm'}}),
    ('梁高改为600mm',{'beam_depth_mm':{'value':600,'unit':'mm','quote':'跨度改为600mm'}}),
    ('梁高改为600mm',{'invented_field':{'value':600,'unit':'mm','quote':'梁高改为600mm'}}),
    ('梁高改为600mm',{'beam_depth_mm':{'value':-1,'unit':'mm','quote':'梁高改为600mm'}}),
    ('梁高改为600mm，跨度改为6m',{'beam_depth_mm':{'value':600,'unit':'m','quote':'梁高改为600mm，跨度改为6m'}}),
    ('梁高改为600mm，跨度改为6m',{'beam_depth_mm':{'value':6,'unit':'m','quote':'梁高改为600mm，跨度改为6m'}}),
])
def test_model_cannot_supply_unquoted_values_fields_or_units(query,change):
    s=session();before=basis_hash(s.result)
    with pytest.raises(ValueError):s.ask_expert(query,client=DecisionClient({'intent':'modify','changes':change}))
    assert basis_hash(s.result)==before and not s.consultations


def test_stale_result_and_dirty_draft_invalidate_proposal():
    s=session();reply=s.ask_expert('梁高改为600mm')
    changed=s.result.model_copy(deep=True);changed.design_revision+=1
    with pytest.raises(ValueError,match='依据已经变化'):apply_proposal(changed,reply)
    s.mark_dirty()
    with pytest.raises(ValueError):s.adopt_expert_proposal(reply.id)
    with pytest.raises(ValueError):s.ask_expert('挠度如何？')


def test_direct_demand_cannot_silently_survive_load_change():
    s=session('仅抗弯局部验算')
    with pytest.raises(ValueError,match='直接设计内力'):s.ask_expert('活载改为6kN/m')
    reply=s.ask_expert('设计弯矩改为110kN·m')
    s.adopt_expert_proposal(reply.id);s.confirm();s.run('offline')
    assert s.result.tool_results['evaluation.flexural_check'].outputs['demand_kn_m']==110


def test_unrequested_check_is_not_inferred_and_unsupported_stays_in_scope():
    s=session('仅抗弯局部验算');reply=s.ask_expert('裂缝通过了吗？')
    assert reply.evidence[0].outputs=={} and '没有该项' in reply.evidence[0].text
    reply=s.ask_expert('改为悬臂梁')
    assert reply.decision.intent=='unsupported' and not reply.preview


def test_history_export_and_failed_provider_keep_engineering_result():
    class ErrorClient:
        def consult(self,*args):raise RuntimeError('SECRET_PROVIDER_HEADER')
    s=session();before=basis_hash(s.result)
    with pytest.raises(ValueError) as exc:s.ask_expert('解释挠度',client=ErrorClient())
    assert 'SECRET' not in str(exc.value)+str(s.calls)
    assert s.stage=='completed' and basis_hash(s.result)==before
    s.ask_expert('解释挠度')
    audit=json.loads(s.downloads()['audit'])
    assert len(audit['consultations'])==1
    s.load(load_case('已有梁独立验算'),'new')
    assert not s.consultations


def test_hosted_contract_uses_only_structured_decision_and_current_evidence():
    class Model:
        def with_structured_output(self, schema, method):
            assert schema is ConsultationDecision
            return self
        def invoke(self, messages):
            data=json.loads(messages[1].content)
            assert data['current']['candidate']=={} and data['query']=='解释挠度'
            return ConsultationDecision(intent='explain',focus=['deflection'])
    reply=consult(session().result,'解释挠度',DeepSeekConsultant(Model()))
    assert reply.evidence[0].tool=='deflection_check'
