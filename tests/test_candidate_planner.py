"""Scripted decisions test boundaries; live model evidence is recorded separately."""
import pytest
from engi_agent.engineering.roles import ProgramRoles,CandidateDecision
from engi_agent.engineering.cn_schema import ParameterValue,CNParameters
from engi_agent.engineering.cn_workflow import prepare,confirm,run_engineering
from engi_agent.engineering.design_search import CandidateSearch
from engi_agent.engineering.preferences import PreferenceSnapshot
from engi_agent.ui.service import WorkbenchSession,load_case


class Decider(ProgramRoles):
    supports_candidate_planning=True
    def __init__(self,decision):self.decision=decision;self.payloads=[]
    def choose_candidate(self,payload):
        self.payloads.append(payload)
        return self.decision


def small_diameter_request():
    r=load_case('完整新方案设计')
    r.parameters['bar_diameter_mm']=ParameterValue(value=14,unit='mm')
    r.search_diameters_mm=[20,22,25];r.max_iterations=2
    return r


def test_model_decision_changes_executed_candidate_and_is_audited(monkeypatch):
    def forbidden(*args):raise AssertionError('模型模式不能调用规则选择下一方案')
    monkeypatch.setattr(CandidateSearch,'propose',forbidden)
    roles=Decider(CandidateDecision(bar_diameter_mm=22,reason='锚固区构造未通过，改用允许的22mm并重新计算根数。'))
    ctl=WorkbenchSession();ctl.load(small_diameter_request(),'planner test');ctl.confirm()
    state=ctl.run('DeepSeek',roles=roles)
    assert len(state.revisions)==2 and state.revisions[1]['parameters']['bar_diameter_mm']==22
    assert state.evaluation.status=='pass'
    assert state.design_search['decision_mode']=='llm'
    assert state.design_search['selection_trace'][0]['status']=='accepted'
    assert roles.payloads[0]['history'][0]['checks']['detailing'] is False
    assert roles.payloads[0]['remaining_attempts']==1
    assert any(c.role=='DesignDecision' and c.status=='success' for c in ctl.calls)
    # An independent existing-beam check must agree with every resulting check.
    check=state.request.model_copy(deep=True);check.task_type='evaluate_existing';check.auto_redesign=False
    for k,v in state.candidate.items():
        if k in CNParameters.model_fields:
            check.parameters[k]=ParameterValue(value=v,unit='mm' if k.endswith('_mm') else None)
    fresh=run_engineering(confirm(prepare(check)),ProgramRoles())
    for name in ('flexural_check','shear_check','detailing_check','crack_check','deflection_check'):
        assert state.tool_results['evaluation.'+name].outputs==fresh.tool_results['evaluation.'+name].outputs


@pytest.mark.parametrize('decision',[
    CandidateDecision(beam_width_mm=325,reason='尝试加宽'),
    CandidateDecision(bar_diameter_mm=18,reason='尝试未授权直径'),
    CandidateDecision(bar_diameter_mm=14,reason='重复当前方案'),
    {'minimum_bar_count':True,'reason':'错误类型'},
])
def test_rejected_decisions_never_execute_or_silently_fall_back(decision):
    state=run_engineering(confirm(prepare(small_diameter_request())),Decider(decision))
    assert len(state.revisions)==1
    assert state.evaluation.status=='error'
    assert state.design_search['selection_trace'][0]['status']=='rejected'
    assert '决策失败' in state.search_stop_reason


def test_preferences_reach_decider_before_any_candidate_passes():
    r=small_diameter_request();r.preference_guidance=True
    r.preference_snapshot=PreferenceSnapshot(weights=(.8,.1,.1))
    roles=Decider(CandidateDecision(bar_diameter_mm=20,reason='结合偏好保持梁高，先尝试换径。'))
    state=run_engineering(confirm(prepare(r)),roles)
    assert roles.payloads[0]['preference']['weights']==(.8,.1,.1)
    assert roles.payloads[0]['history'][0]['status']=='fail'
    assert state.evaluation.status=='pass'


def test_agent_can_choose_different_free_section_step_and_reject_invalid_step():
    r=load_case('截面与配筋联合设计');r.max_iterations=2
    roles=Decider(CandidateDecision(beam_width_mm=300,beam_depth_mm=575,bar_diameter_mm=22,reason='尝试更宽截面及25mm离散梁高。'))
    state=run_engineering(confirm(prepare(r)),roles)
    assert state.revisions[1]['parameters']['beam_depth_mm']==575
    invalid=Decider(CandidateDecision(beam_depth_mm=576,reason='非允许步长'))
    rejected=run_engineering(confirm(prepare(r)),invalid)
    assert len(rejected.revisions)==1 and rejected.evaluation.status=='error'


def test_agent_can_stop_but_cannot_claim_failed_design_passed():
    roles=Decider(CandidateDecision(stop=True,reason='需要工程师补充构造条件'))
    state=run_engineering(confirm(prepare(small_diameter_request())),roles)
    assert len(state.revisions)==1 and state.evaluation.status=='fail'
    assert 'Design Agent决定停止' in state.search_stop_reason
    assert state.design_search['selection_trace'][0]['status']=='stopped'


def test_model_exception_is_visible_and_does_not_trigger_rule_search():
    class Broken(Decider):
        def choose_candidate(self,payload):raise RuntimeError('provider failure')
    state=run_engineering(confirm(prepare(small_diameter_request())),Broken(None))
    assert len(state.revisions)==1 and state.evaluation.status=='error'
    assert state.design_search['selection_trace'][0]['error_type']=='RuntimeError'
