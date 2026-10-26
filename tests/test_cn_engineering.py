"""Code arithmetic, dependency integrity and independent evaluation boundaries."""
import json
import math
from pathlib import Path
import pytest
from engi_agent.engineering.schema import TaskRequest, ParameterValue, EngineeringState
from engi_agent.engineering.workflow import prepare, confirm, run_engineering
from engi_agent.engineering.roles import FixtureRoles, RolePlan, DeepSeekRoles
from engi_agent.engineering.cn_workflow import revise
from engi_agent.engineering import cn_tools
from engi_agent.engineering.reporting import markdown_report

ROOT=Path(__file__).resolve().parents[1]


def request(name='cn_design'):
    return TaskRequest.model_validate_json((ROOT/'examples/engineering'/f'{name}.json').read_text(encoding='utf-8'))


def run(r):
    return run_engineering(confirm(prepare(r)),FixtureRoles(r))


def setp(r,k,v,unit=None):
    r.parameters[k]=ParameterValue(value=v,unit=unit)
    return r


def out(s,name,phase='evaluation'):
    return s.tool_results[f'{phase}.{name}'].outputs


def test_full_design_existing_and_independent_values():
    s=run(request()); e=run(request('cn_existing'))
    assert s.evaluation.status==e.evaluation.status=='pass'
    assert s.candidate['bar_count']==3
    assert out(s,'materials')['fc_mpa']==14.3  # C30 design strength, not cylinder 30 MPa
    assert out(s,'section_geometry')['effective_depth_mm']==502
    assert out(s,'load_combination')['added_self_weight_kn_m']==pytest.approx(4.125)
    assert out(s,'beam_analysis')['Mu_kn_m']==pytest.approx(116.38125)
    assert out(s,'beam_analysis')['Vu_design_kn']==pytest.approx(64.65625)
    assert out(s,'flexural_check')['minimum_steel_mm2']==330
    assert out(s,'flexural_check')['capacity_kn_m']==pytest.approx(156.90745,abs=0.00001)
    # Independent Newton-mm arithmetic: 3*100*pi mm², fy=360, fc=14.3, b=300.
    area=300*math.pi; x=360*area/(14.3*300)
    assert out(s,'flexural_check')['capacity_kn_m']==pytest.approx(360*area*(502-x/2)/1e6)
    assert out(e,'flexural_check')['capacity_kn_m']==out(s,'flexural_check')['capacity_kn_m']
    assert all(k in s.tool_results for k in ['design.materials','evaluation.materials'])


def test_crack_and_long_term_independent_hand_chain():
    s=run(request()); c=out(s,'crack_check'); f=out(s,'deflection_check')
    # Written hand chain in docs/cn_reference_case.md, distinct unit conversion boundary.
    area=3*math.pi*.02**2/4 # m²
    mq=(10+25*.3*.55+.5*5)*6**2/8 # kN*m
    sigma=mq*1000/(.87*.502*area)/1e6 # MPa
    rho_te=area/(.5*.3*.55)
    psi=max(.2,min(1,1.1-.65*2.01/(rho_te*sigma)))
    crack=1.9*psi*sigma/200000*(1.9*38+.08*20/rho_te)
    bs=200e9*area*.502**2/(1.15*psi+.2+6*(200/30)*area/(.3*.502)) # N*m²
    delta=5*16625*6**4/(384*(bs/2))*1000
    assert c['crack_width_mm']==pytest.approx(crack)
    assert f['deflection_mm']==pytest.approx(delta)
    assert f['theta']==2
    assert c['combination']=='准永久组合Gk+ψqQk'


def test_direct_moment_partial_has_no_load_requirements_or_unrelated_steps():
    s=run(request('cn_flexure_only'))
    assert s.evaluation.status=='pass'
    assert s.evaluation.overall_status=='incomplete'
    assert s.execution_plan==['evaluation.'+x for x in ['section_sizing','section_geometry','materials','demand','flexural_check']]
    assert out(s,'demand')['moment_source']=='用户确认设计值'


@pytest.mark.parametrize('key,value,unit',[('span_mm',6,'m'),('beam_width_mm',30,'cm'),('design_moment_kn_m',100000000,'N·mm')])
def test_unit_conversion(key,value,unit):
    r=request('cn_flexure_only'); setp(r,key,value,unit)
    assert run(r).evaluation.status=='pass'


@pytest.mark.parametrize('key,value,unit',[('span_mm',-1,'mm'),('live_quasi_factor',1.2,None),
    ('bar_count',2.5,None),('concrete_grade','C20',None),('environment_class','II',None),
    ('span_mm',6,'MPa'),('support_type','cantilever',None),('safety_class',1,None)])
def test_invalid_values_or_unsupported_input_rejected(key,value,unit):
    r=request(); setp(r,key,value,unit)
    with pytest.raises(ValueError): prepare(r)


def test_missing_load_stops_before_any_calculation_and_unsized_works():
    r=request(); r.parameters.pop('live_load_kn_m')
    p=prepare(r); assert 'live_load_kn_m' in p.missing_parameters
    with pytest.raises(ValueError): confirm(p)
    r=request(); r.parameters.pop('beam_depth_mm'); r.parameters.pop('beam_width_mm')
    s=run(r)
    assert out(s,'section_sizing','design')['beam_depth_mm']==500
    assert s.evaluation.status in ('pass','fail')


def test_confirmed_state_mutation_does_not_compute():
    r=request(); s=confirm(prepare(r)); s.request.parameters['span_mm'].value=7000.0
    s=run_engineering(s,FixtureRoles(r))
    assert s.evaluation.status=='error' and not s.tool_results


def test_included_weight_not_counted_twice():
    a=run(request()); r=request(); setp(r,'self_weight_mode','included'); setp(r,'dead_load_kn_m',14.125,'kN/m')
    b=run(r)
    assert out(a,'beam_analysis')==out(b,'beam_analysis')
    assert out(b,'load_combination')['added_self_weight_kn_m']==0


@pytest.mark.parametrize('mode',['included','excluded'])
def test_height_revision_cache_and_full_recompute_match(mode):
    r=request('cn_existing'); setp(r,'self_weight_mode',mode)
    first=run(r)
    pending=revise(first,{'beam_depth_mm':{'value':600,'unit':'mm'}})
    assert not pending.confirmed
    blocked=run_engineering(pending,FixtureRoles(pending.request)); assert blocked.evaluation.status=='error'
    second=run_engineering(confirm(pending),FixtureRoles(pending.request))
    full=run(pending.request)
    assert second.evaluation==full.evaluation
    for key,result in second.tool_results.items(): assert result.outputs==full.tool_results[key].outputs
    trace={x['tool']:x['action'] for x in second.plan_trace}
    assert trace['materials']=='reuse'
    assert trace['section_geometry']=='invalidate_execute'
    assert trace['load_combination']==('reuse' if mode=='included' else 'invalidate_execute')
    assert trace['beam_analysis']==('reuse' if mode=='included' else 'invalidate_execute')


def test_rebar_count_revision_does_not_rerun_loads_or_geometry():
    s=run(request('cn_existing'))
    revised=confirm(revise(s,{'bar_count':{'value':4}}))
    result=run_engineering(revised,FixtureRoles(revised.request))
    trace={x['tool']:x['action'] for x in result.plan_trace}
    assert trace['section_geometry']==trace['load_combination']=='reuse'
    assert trace['flexural_check']==trace['deflection_check']=='invalidate_execute'


def test_direct_moment_height_change_reuses_demand_and_materials():
    s=run(request('cn_flexure_only'))
    revised=confirm(revise(s,{'beam_depth_mm':{'value':600,'unit':'mm'}}))
    second=run_engineering(revised,FixtureRoles(revised.request))
    trace={x['tool']:x['action'] for x in second.plan_trace}
    assert trace['demand']=='reuse' and 'beam_analysis' not in trace


def test_failed_check_is_not_tool_error_and_automatic_redesign_is_bounded():
    r=request('cn_redesign'); r.auto_redesign=False
    first=run(r); assert first.evaluation.status=='fail'
    assert not first.evaluation.checks['deflection']
    s=run(request('cn_redesign'))
    assert s.evaluation.status=='pass' and s.candidate['bar_count']==4
    assert [x['candidate']['bar_count'] for x in s.revisions]==[3,4]
    assert s.revisions[0]['evaluation']['status']=='fail'
    s=run(request('cn_no_solution'))
    assert s.evaluation.status=='fail' and len(s.revisions)==3
    assert s.errors and s.candidate['beam_depth_mm']==550


def test_flexural_shortfall_spacing_crack_and_deflection_failures():
    r=request('cn_existing'); setp(r,'design_moment_kn_m',200,'kN·m'); assert not run(r).evaluation.checks['flexure']
    r=request('cn_existing'); setp(r,'bar_count',8); assert not run(r).evaluation.checks['detailing']
    r=request('cn_existing'); setp(r,'crack_limit_mm',.01,'mm'); assert not run(r).evaluation.checks['crack']
    r=request('cn_existing'); setp(r,'deflection_limit_ratio',1000); assert not run(r).evaluation.checks['deflection']


def test_material_requirement_and_anchor_failure_are_not_pass():
    r=request(); setp(r,'concrete_grade','C25'); setp(r,'steel_grade','HRB500')
    assert run(r).evaluation.status!='pass'
    r=request('cn_existing'); setp(r,'end_anchor_stirrup_spacing_mm',150,'mm')
    assert not run(r).evaluation.checks['detailing']


def test_model_format_and_api_failure_no_pass():
    class Bad:
        def plan(self,*a,**k): return {'steps':['arbitrary_code'],'explanation':'bad'}
    class Unavailable:
        def plan(self,*a,**k): raise RuntimeError('private provider response')
    r=request()
    for role in (Bad(),Unavailable()):
        s=run_engineering(confirm(prepare(r)),role)
        assert s.evaluation.status=='error'
        assert not s.tool_results
        assert 'private provider response' not in str(s.errors)


def test_tool_exception_blocks_only_descendants(monkeypatch):
    def error(*args): raise ArithmeticError('injected')
    monkeypatch.setitem(cn_tools.REGISTRY,'load_combination',error)
    s=run(request('cn_existing'))
    assert s.evaluation.status=='error'
    assert s.tool_results['evaluation.crack_check'].status=='blocked'
    assert s.tool_results['evaluation.detailing_check'].status=='success'


def test_zero_service_load_and_rho_te_crack_clamp_only():
    r=request('cn_existing'); setp(r,'self_weight_mode','included'); setp(r,'dead_load_kn_m',0,'kN/m'); setp(r,'live_load_kn_m',0,'kN/m')
    s=run(r)
    assert out(s,'crack_check')['crack_width_mm']==out(s,'deflection_check')['deflection_mm']==0
    setp(r,'bar_count',2); s=run(r)
    assert out(s,'crack_check')['rho_te']==.01
    assert out(s,'deflection_check')['rho_te']<.01


def test_serialization_and_engineer_readable_report():
    s=run(request('cn_redesign'))
    restored=EngineeringState.model_validate_json(s.model_dump_json())
    assert restored.profile.version=='cn-rc-2024-v1'
    report=markdown_report(restored,'case.json')
    assert all(x in report for x in ('参数','独立验算','裂缝','长期挠度','复用','方案修订','未覆盖'))
    assert '教学试算报告' not in report


def test_cn_cli_current_process_revision(tmp_path,monkeypatch,capsys):
    from engi_agent.engineering.cli import main
    answers=iter(['确认','修改 梁高 600 mm','确认','quit'])
    monkeypatch.setattr('builtins.input',lambda _:next(answers))
    # interactive_confirm binds input at import time; replace that function's default too.
    from engi_agent.engineering import cli
    monkeypatch.setattr(cli.interactive_confirm,'__defaults__',(lambda _:next(answers),print))
    result=main(['--engineering','--offline','--request',str(ROOT/'examples/engineering/cn_existing.json'),
                 '--session','--output-dir',str(tmp_path)])
    assert result==0
    files=list(tmp_path.glob('*.json')); assert len(files)==2
    states=[EngineeringState.model_validate_json(p.read_text(encoding='utf-8')) for p in files]
    latest=max(states,key=lambda s:s.design_revision)
    assert latest.design_revision==2 and len(latest.revisions)==2
    assert any(t['action']=='reuse' for t in latest.plan_trace)


def test_bad_numerical_output_and_version_change(monkeypatch):
    from engi_agent.engineering.dependency_graph import SPECS
    from dataclasses import replace
    s=run(request('cn_existing'))
    changed=confirm(revise(s,{}))
    monkeypatch.setitem(SPECS,'flexural_check',replace(SPECS['flexural_check'],version='test-version-2'))
    second=run_engineering(changed,FixtureRoles(changed.request))
    assert next(t for t in second.plan_trace if t['tool']=='flexural_check')['action']=='invalidate_execute'
    monkeypatch.setitem(cn_tools.REGISTRY,'flexural_check',lambda *a:{'pass':True,'reasons':[]})
    assert run(request('cn_existing')).evaluation.status=='error'


def test_chinese_class_is_normalized_and_raw_value_retained():
    r=request();setp(r,'safety_class','二级')
    s=prepare(r)
    assert s.request.parameters['safety_class'].value=='2'
    assert s.request.parameters['safety_class'].raw_value=='二级'


def test_teaching_mode_rejects_cn_target_instead_of_empty_pass():
    r=TaskRequest.model_validate_json((ROOT/'examples/engineering/metric_existing.json').read_text(encoding='utf-8'))
    r.targets=['crack']
    with pytest.raises(ValueError): prepare(r)


def test_only_flexure_does_not_require_unrelated_self_weight_fields():
    r=request('cn_flexure_only')
    r.parameters.pop('self_weight_mode');r.parameters.pop('concrete_unit_weight_kn_m3')
    assert run(r).evaluation.status=='pass'


def test_flexure_from_load_without_support_width_does_not_invent_edge_shear():
    r=request('cn_existing');r.targets=['flexure'];r.parameters.pop('support_width_mm')
    s=run(r)
    assert s.evaluation.status=='pass'
    assert out(s,'beam_analysis')['Vu_design_kn'] is None
    assert 'shear_check' not in s.evaluation.checks


def test_explicit_template_and_natural_query_entry(tmp_path,monkeypatch,capsys):
    from engi_agent.engineering import cli
    parsed=TaskRequest(code='cn-2024',task_type='new_design',parameters={'span_mm':ParameterValue(value=6,unit='m',source='llm_extracted')})
    monkeypatch.setattr(cli,'DeepSeekRoles',lambda:FixtureRoles(parsed))
    result=cli.main(['--engineering','--base-request',str(ROOT/'examples/engineering/cn_design.json'),
        '--query','按中国规范新设计一根梁，跨度6m，其余采用模板','--approve','--output-dir',str(tmp_path)])
    assert result==0
    s=EngineeringState.model_validate_json(next(tmp_path.glob('*.json')).read_text(encoding='utf-8'))
    assert s.request.parameters['concrete_grade'].source=='template'
    assert s.request.parameters['span_mm'].source=='llm_extracted'


def test_cn_unsupported_request_report_cannot_pass():
    s=run_engineering(prepare(TaskRequest(code='cn-2024',task_type='unsupported')),FixtureRoles(request()))
    assert s.evaluation.status=='incomplete'
    assert '请求项目通过' not in markdown_report(s)
