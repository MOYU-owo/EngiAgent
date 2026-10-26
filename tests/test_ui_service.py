"""Real engineering scenarios through the UI adapter; no browser and no API costs."""
import json
from pathlib import Path
from xml.etree import ElementTree
import pytest
from engi_agent.engineering.schema import TaskRequest
from engi_agent.engineering.roles import FixtureRoles
from engi_agent.ui.service import WorkbenchSession, load_case, CASES, ROOT
from engi_agent.ui.projections import (GROUPS,editor_rows,result_rows,dag_nodes,revision_comparison)
from engi_agent.ui.diagrams import beam_svg,dag_dot,agent_dot

REFERENCES=json.loads((Path(__file__).parent/'data/ui_reference.json').read_text(encoding='utf-8'))


def rows(session):
    return [r for group in GROUPS for r in editor_rows(session.draft,group)]


def run_case(name):
    session=WorkbenchSession()
    session.load(load_case(name),name)
    session.confirm();session.run('offline')
    return session


@pytest.mark.parametrize('name',list(CASES)[:-1])
def test_actual_scenarios_match_existing_json_and_download(name):
    session=run_case(name)
    reference=REFERENCES[CASES[name]]
    assert session.result.evaluation.model_dump()==reference['evaluation']
    assert session.result.candidate==reference['candidate']
    for key,result in session.result.tool_results.items():
        assert result.outputs==reference['tool_results'][key]['outputs']
    data=session.downloads()
    assert json.loads(data['json'])==session.result.model_dump()
    assert 'EngiAgent' in data['md'].decode('utf-8')
    assert session.completed_runs==1 and session.stage=='completed'
    # Pure reads, graphs and report downloads do not trigger additional calls.
    calls=len(session.calls)
    for _ in range(2):
        session.downloads();result_rows(session.result);dag_nodes(session.result,'evaluation',-1)
    assert len(session.calls)==calls
    with pytest.raises(ValueError):session.run('offline')


def test_height_revision_reuses_real_cache_and_matches_sixth_case():
    session=run_case('已有梁独立验算')
    session.mark_dirty()
    assert not session.draft.confirmed
    with pytest.raises(ValueError):session.run('offline')
    edit=rows(session)
    next(r for r in edit if r['字段']=='beam_depth_mm')['输入值']='600'
    session.apply(edit,'evaluate_existing',session.draft.request.targets,False,3)
    assert session.stage=='validated' and not session.draft.confirmed
    session.confirm();session.run('offline')
    reference=REFERENCES['cn_height_revision']
    for key,result in session.result.tool_results.items(): assert result.outputs==reference['tool_results'][key]['outputs']
    assert session.result.design_revision==2
    nodes=dag_nodes(session.result,'evaluation',-1)
    assert next(n for n in nodes if n['name']=='materials')['state']=='reuse'
    assert next(n for n in nodes if n['name']=='load_combination')['action']=='失效重算'
    changed=revision_comparison(session.result,0,1)
    assert any(row['参数']=='梁高' for row in changed)


def test_missing_invalid_and_unconfirmed_are_blocked():
    session=WorkbenchSession();session.load(load_case('完整新方案设计'),'test')
    values=rows(session);next(r for r in values if r['字段']=='live_load_kn_m')['输入值']=''
    session.apply(values,'new_design',session.draft.request.targets,False,3)
    assert 'live_load_kn_m' in session.draft.missing_parameters
    with pytest.raises(ValueError):session.confirm()
    next(r for r in values if r['字段']=='live_load_kn_m')['输入值']='-1'
    with pytest.raises(ValueError):session.apply(values,'new_design',session.draft.request.targets,False,3)
    assert session.stage=='editing'
    with pytest.raises(ValueError):session.run('offline')


def test_bad_model_and_api_error_never_show_pass_or_secret():
    class APIError:
        def parse(self,*a):raise RuntimeError('SECRET_PROVIDER_HEADER')
        def plan(self,*a):raise RuntimeError('SECRET_PROVIDER_HEADER')
    session=WorkbenchSession()
    with pytest.raises(ValueError):session.parse('设计一根梁',roles=APIError())
    assert 'SECRET' not in str(session.errors)+str(session.calls)
    session.load(load_case('完整新方案设计'),'test');session.confirm()
    session.run('DeepSeek',roles=APIError())
    assert session.result.evaluation.status=='error'
    assert session.result.evaluation.overall_status=='incomplete'
    assert session.calls[-1].status=='error'
    assert 'SECRET' not in str(session.calls)


def test_parse_runs_once_preserves_source_and_raw_values():
    base=load_case('完整新方案设计')
    parsed=TaskRequest(code='cn-2024',task_type='new_design',parameters={'span_mm':{'value':6,'unit':'m'}})
    session=WorkbenchSession()
    session.parse('跨度6m，其余采用模板',base,FixtureRoles(parsed))
    assert len(session.calls)==1
    assert session.draft.request.parameters['span_mm'].raw_value==6
    assert session.draft.request.parameters['span_mm'].value==6000
    assert session.draft.request.parameters['concrete_grade'].source=='template'
    assert session.result is None


def test_dag_only_actual_subgraph_and_no_fake_pending_design():
    session=run_case('仅抗弯局部验算')
    nodes=dag_nodes(session.result,'evaluation',0)
    names={n['name'] for n in nodes}
    assert names=={'materials','section_sizing','section_geometry','demand','flexural_check'}
    assert dag_nodes(session.result,'design',0)==[]
    for node in nodes:assert set(node['parents'])<=names
    dot=dag_dot(nodes,'materials')
    assert 'shear_check' not in dot and 'crack_check' not in dot


def test_svg_uses_actual_data_and_does_not_guess_missing_values():
    svg=beam_svg({'span_mm':6000,'beam_width_mm':300,'beam_depth_mm':550})
    ElementTree.fromstring(svg)
    assert '6,000' in svg and '300' in svg
    assert '未提供线荷载' in svg and '待确定' in svg
    assert '<circle' not in svg
    assert '未绘制梁立面' in beam_svg({})


def test_agent_edges_do_not_label_new_user_run_as_failure_feedback():
    session=run_case('挠度超限后有限改设')
    dot=agent_dot([vars(c) for c in session.calls])
    assert '失败反馈' in dot
    # A later separate confirmed request is not an internal failure loop.
    calls=[{'role':'Evaluation','mode':'offline','status':'success','run_id':1},
           {'role':'Design','mode':'offline','status':'success','run_id':2}]
    assert '失败反馈' not in agent_dot(calls)


def test_interrupted_run_is_not_left_running_or_automatically_retried():
    class Interrupted:
        def plan(self,*args):raise KeyboardInterrupt()
    session=WorkbenchSession();session.load(load_case('完整新方案设计'),'test');session.confirm()
    with pytest.raises(KeyboardInterrupt):session.run('DeepSeek',roles=Interrupted())
    assert session.stage=='error' and session.result is None
    assert session.calls[-1].status=='error'
    with pytest.raises(ValueError):session.run('DeepSeek',roles=Interrupted())


def test_tool_error_projection_is_not_a_pass(monkeypatch):
    from engi_agent.engineering import cn_tools
    def fail(*args):raise ArithmeticError('injected')
    monkeypatch.setitem(cn_tools.REGISTRY,'crack_check',fail)
    session=run_case('已有梁独立验算')
    assert session.result.evaluation.status=='error'
    row=next(r for r in result_rows(session.result) if r['检查项目']=='裂缝')
    assert row['工具执行']=='执行失败' and row['分项结论']=='未获得有效结论'
    assert next(n for n in dag_nodes(session.result,'evaluation',-1) if n['name']=='crack_check')['state']=='error'
