import itertools
import json
import subprocess
import sys
import pytest
from engi_agent.ui.service import WorkbenchSession,load_case
from engi_agent.ui.preference_panel import simulate_evaluations,chart_rows
from engi_agent.engineering.preferences import PreferenceStore,PreferenceSnapshot,pool,score,nondominated
from engi_agent.engineering.cn_workflow import confirm,prepare,run_engineering
from engi_agent.engineering.roles import ProgramRoles


@pytest.fixture
def session(tmp_path,monkeypatch):
    monkeypatch.setenv('ENGIAGENT_PREFERENCE_DIR',str(tmp_path/'profiles'))
    ctl=WorkbenchSession();ctl.load(load_case('截面与配筋联合设计'),'test');ctl.confirm();ctl.run('program')
    return ctl


def test_pair_learning_changes_weights_and_isolates_sources(session):
    items=pool(session.result)
    a,b=next((a,b) for a,b in itertools.combinations(items,2) if a['features']!=b['features'])
    real=PreferenceStore('real');before,_=real.load()
    after=real.evaluate(session.result,a['id'],b['id'],a['id'],before.version)
    assert after.weights!=before.weights and after.version==1
    assert min(after.weights)>=0 and sum(after.weights)==pytest.approx(1)
    assert PreferenceStore('simulated').load()[0].version==0
    assert a['features']==pytest.approx([a['raw'][0]/1000,a['raw'][1]/1000,a['raw'][2]])
    assert real.load()[1][0]['source']=='real'
    with pytest.raises(ValueError):real.evaluate(session.result,a['id'],b['id'],a['id'],0)
    with pytest.raises(ValueError):real.evaluate(session.result,'unverified',b['id'],b['id'],1)


def test_restart_and_online_search_order_not_only_display_ranking(session):
    before=PreferenceStore('simulated').load()[0]
    trained=simulate_evaluations(session.result)
    assert trained.weights!=before.weights and trained.version==20
    output=subprocess.check_output([sys.executable,'-c',
        "from engi_agent.engineering.preferences import PreferenceStore;print(PreferenceStore('simulated').load()[0].model_dump_json())"],text=True)
    restarted=PreferenceSnapshot.model_validate_json(output)
    assert restarted==trained
    comparison=session.compare_preferences('simulated')
    off,on=(comparison['results'][k] for k in ('off','on'))
    def seq(r):return [h['candidate'] for h in r['state']['revisions']]
    assert seq(off)!=seq(on) and seq(off)[:3]==seq(on)[:3]
    assert off['metrics']['tested']==on['metrics']['tested']==12
    equal=session.result.request.model_copy(deep=True)
    equal.preference_guidance=True;equal.preference_snapshot=PreferenceSnapshot(source='simulated')
    uniform=run_engineering(confirm(prepare(equal)),ProgramRoles())
    assert [h['candidate'] for h in uniform.revisions]!=seq(on)
    assert on['metrics']['best_score']<off['metrics']['best_score']
    trace=on['state']['design_search']['selection_trace']
    assert any(t['mode']=='rule_exploration' for t in trace)
    for index,t in enumerate(trace):
        if t['mode']=='preference_neighbour':
            # Trace index 0 proposes round 2; parents must already be checked.
            parent=next(h for h in on['state']['revisions'] if h['revision']==t['anchor_revision'])
            assert parent['iteration']<=index+1 and parent['evaluation']['status']=='pass'
            assert t['verified_anchor_features'] and t['anchor_score'] is not None
            assert 'utilization' not in t['parameters']
    assert PreferenceStore('real').load()[0].version==0


def test_guidance_default_off_and_checks_match_fresh_calculation(session):
    assert not session.result.request.preference_guidance
    simulate_evaluations(session.result)
    session.configure_preference(True,'simulated');session.confirm();state=session.run('program')
    assert state.design_search['preference_snapshot']['source']=='simulated'
    from engi_agent.engineering.cn_schema import ParameterValue,CNParameters
    r=state.request.model_copy(deep=True);r.preference_guidance=False;r.preference_snapshot=None
    r.task_type='evaluate_existing';r.auto_redesign=False
    for k,v in state.candidate.items():
        if k in CNParameters.model_fields:r.parameters[k]=ParameterValue(value=v,unit='mm' if k.endswith('_mm') else None)
    fresh=run_engineering(confirm(prepare(r)),ProgramRoles())
    for name in ('flexural_check','shear_check','detailing_check','crack_check','deflection_check'):
        assert state.tool_results['evaluation.'+name].outputs==fresh.tool_results['evaluation.'+name].outputs


def test_chart_front_uses_verified_three_dimensional_data(session):
    items=pool(session.result);front=nondominated(items)
    assert front and len(front)<=len(items)
    rows=chart_rows(session.result,PreferenceSnapshot(),'off')
    assert len(rows)==len(items) and all(r['utilization']<=1 for r in rows)
    assert sum(r['front'] for r in rows)==len(front)


def test_scatter_passes_column_records_to_streamlit(session,monkeypatch):
    from engi_agent.ui import preference_panel as panel
    captured=[]
    monkeypatch.setattr(panel.st,'vega_lite_chart',lambda data,spec,**kw:captured.append(data))
    monkeypatch.setattr(panel.st,'caption',lambda *a:None)
    rows=chart_rows(session.result,PreferenceSnapshot(),'off');panel.scatter(rows)
    assert captured[0]==rows and isinstance(captured[0],list)
    assert all('height' in r and 'steel' in r for r in captured[0])


def test_corrupt_or_mixed_memory_is_not_silently_loaded(session):
    simulate_evaluations(session.result,1)
    store=PreferenceStore('simulated');data=json.loads(store.path.read_text(encoding='utf-8'))
    data['snapshot']['source']='real';store.path.write_text(json.dumps(data),encoding='utf-8')
    with pytest.raises(ValueError):store.load()
    with pytest.raises(ValueError):PreferenceSnapshot(weights=(-1,1,1))
    with pytest.raises(ValueError):PreferenceSnapshot(normalization='other')
