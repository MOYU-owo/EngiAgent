"""Reproduces the supplied failed design and verifies repair/selection evidence."""
import math
import pytest
from engi_agent.engineering.cn_schema import ParameterValue, TaskRequest
from engi_agent.engineering.cn_workflow import prepare, confirm, run_engineering, revise
from engi_agent.engineering.roles import ProgramRoles
from engi_agent.ui.service import WorkbenchSession
from pathlib import Path
import runpy
report_request=runpy.run_path(str(Path(__file__).resolve().parents[1]/'examples/reproduce_report_feedback.py'))['report_request']


def run(r):
    return run_engineering(confirm(prepare(r)),ProgramRoles())


@pytest.mark.parametrize('key', ['bar_diameter_mm','stirrup_diameter_mm','top_bar_diameter_mm','side_bar_diameter_mm'])
@pytest.mark.parametrize('value,unit', [(11,'mm'),(.011,'m')])
def test_arbitrary_diameter_is_rejected_after_unit_conversion(key,value,unit):
    r=report_request();r.parameters[key]=ParameterValue(value=value,unit=unit)
    with pytest.raises(ValueError,match='公称直径目录'):prepare(r)


def test_hpb_stirrup_catalog_and_zero_side_bar_semantics():
    r=report_request();r.parameters['stirrup_diameter_mm']=ParameterValue(value=28,unit='mm')
    with pytest.raises(ValueError):prepare(r)
    r=report_request();r.parameters['side_bar_diameter_mm']=ParameterValue(value=0,unit='mm')
    assert prepare(r).request.parameters['side_bar_diameter_mm'].value==0


def test_report_case_trace_matches_independent_crack_chain_and_failure():
    r=report_request();r.auto_redesign=False;s=run(r)
    crack=s.tool_results['evaluation.crack_check']
    area=3*math.pi*20**2/4;d=550-35-8-20/2
    mq=(20+25*.3*.55+.5*5)*6**2/8
    sigma=mq*1e6/(.87*d*area);rho=max(area/(.5*300*550),.01)
    psi=max(.2,min(1,1.1-.65*2.64/(rho*sigma)))
    expected=1.9*psi*sigma/200000*(1.9*43+.08*20/rho)
    assert crack.outputs['crack_width_mm']==pytest.approx(expected)
    assert expected==pytest.approx(.3648685131517939)
    steps=crack.calculation_steps
    assert any(row['title']=='裂缝宽度' and row['result']==pytest.approx(expected) for row in steps)
    assert steps[-1]['passed'] is False and '未开启' in s.search_stop_reason
    assert all(result.calculation_steps for result in s.tool_results.values())


def test_crack_failure_repairs_without_changing_fixed_inputs_or_limits():
    r=report_request();r.auto_redesign=True;s=run(r)
    assert [h['evaluation']['status'] for h in s.revisions]==['fail','pass']
    assert s.candidate['bar_count']==4 and s.evaluation.status=='pass'
    assert all(s.evaluation.checks.values())
    assert s.request.parameters==confirm(prepare(r)).request.parameters
    assert s.candidate['beam_depth_mm']==550 and s.candidate['bar_diameter_mm']==20


def test_two_verified_candidates_selection_and_new_revision_keep_correct_evidence():
    r=report_request();r.auto_redesign=True;r.search_diameters_mm=[20,22];r.solution_count=2;r.max_iterations=6
    session=WorkbenchSession();session.load(r,'report');session.confirm();session.run('program')
    s=session.result
    assert len(s.design_alternatives)==2
    assert s.candidate['bar_count']==3 and s.candidate['bar_diameter_mm']==22
    assert s.tool_results['evaluation.crack_check'].outputs['crack_width_mm']==pytest.approx(.28530075940340266)
    count=len(session.calls)
    with pytest.raises(ValueError):session.select_design_alternative(1)
    session.select_design_alternative(2)
    assert session.result.candidate['bar_count']==4 and session.result.candidate['bar_diameter_mm']==20
    assert len(session.calls)==count+1 and session.calls[-1].mode=='user_selection'
    assert session.completed_runs==1
    future=revise(session.result,{'beam_depth_mm':{'value':600,'unit':'mm'}})
    assert future.design_revision>max(h['revision'] for h in s.revisions)


def test_passing_candidate_is_retained_if_later_attempts_fail():
    r=report_request();r.auto_redesign=True;r.search_diameters_mm=[25];r.solution_count=3;r.max_iterations=3
    s=run(r)
    assert s.revisions[-1]['evaluation']['status']=='fail'
    assert s.evaluation.status=='pass' and s.candidate['bar_diameter_mm']==20
    assert s.design_revision==2 and not s.errors
    assert '上限' in s.search_stop_reason


def test_new_design_defaults_to_repair_and_existing_defaults_to_evaluation():
    assert TaskRequest(task_type='new_design').auto_redesign
    assert not TaskRequest(task_type='evaluate_existing').auto_redesign
    assert not TaskRequest(task_type='new_design',auto_redesign=False).auto_redesign
    with pytest.raises(ValueError):TaskRequest(task_type='new_design',search_diameters_mm=[11])
