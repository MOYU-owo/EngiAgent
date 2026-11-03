"""Streamlit widget flows; no hosted model calls. Run when ui extras are installed."""
from pathlib import Path
import pytest
pytest.importorskip('streamlit')
from streamlit.testing.v1 import AppTest
from engi_agent.ui.service import CASES

ROOT=Path(__file__).resolve().parents[1]


def app(case='完整新方案设计'):
    at=AppTest.from_file(str(ROOT/'streamlit_app.py'),default_timeout=30).run()
    at.selectbox(key='case_selector').select(case).run()
    at.button(key='load_case').click().run()
    assert not at.exception
    return at


@pytest.mark.parametrize('case',list(CASES)[:-1])
def test_web_five_cases_and_navigation_never_reexecute(case):
    at=app(case)
    assert at.button(key='run').disabled
    at.button(key='confirm').click().run()
    assert not at.button(key='run').disabled
    at.button(key='run').click().run()
    assert not at.exception
    ctl=at.session_state['workbench']
    assert ctl.result.evaluation.status==('fail' if case=='改设达到上限停止' else 'pass')
    calls=len(ctl.calls)
    assert at.button(key='run').disabled
    for page in ('计算与规范复核','Agent 与动态规划','专家咨询','对照实验','设计工作台'):
        at.radio(key='nav').set_value(page).run()
        assert not at.exception
        assert len(at.session_state['workbench'].calls)==calls
    at.run()
    assert at.session_state['workbench'].completed_runs==1
    assert len(at.session_state['workbench'].calls)==calls


def test_web_height_edit_requires_validation_confirmation_and_reuses():
    at=app('已有梁独立验算')
    at.button(key='confirm').click().run();at.button(key='run').click().run()
    ctl=at.session_state['workbench'];g=ctl.editor_generation
    # Set the documented data_editor widget edit state, including its dirty callback.
    ctl.mark_dirty()
    at.session_state[f'editor_几何_{g}']={'edited_rows':{2:{'输入值':'600'}},'added_rows':[],'deleted_rows':[]}
    at.run()
    assert at.button(key='run').disabled and at.button(key='confirm').disabled
    at.button(key='validate').click().run()
    assert not at.exception
    assert at.session_state['workbench'].draft.request.parameters['beam_depth_mm'].value==600
    at.button(key='confirm').click().run();at.button(key='run').click().run()
    assert not at.exception
    final=at.session_state['workbench'].result
    assert final.design_revision==2
    assert next(t for t in final.plan_trace if t['tool']=='materials')['action']=='reuse'


def test_web_pending_graph_and_experiment_are_truthful():
    at=app('仅抗弯局部验算')
    at.radio(key='nav').set_value('Agent 与动态规划').run()
    assert not at.exception
    assert at.session_state['workbench'].result is None
    at.radio(key='nav').set_value('对照实验').run()
    assert not at.exception
    assert any('未执行' in alert.value for alert in at.info)


def test_web_consultation_adopt_confirm_and_recompute():
    at=app('已有梁独立验算')
    at.button(key='confirm').click().run();at.button(key='run').click().run()
    at.radio(key='nav').set_value('专家咨询').run()
    at.text_area(key='expert_query').set_value('梁高改为600mm').run()
    at.button(key='ask_expert').click().run()
    assert not at.exception
    ctl=at.session_state['workbench'];reply=ctl.consultations[-1]
    calls=len(ctl.calls)
    at.run();assert len(ctl.calls)==calls
    at.button(key='adopt_'+reply['id']).click().run()
    assert not at.exception and ctl.stage=='validated'
    at.radio(key='nav').set_value('设计工作台').run()
    assert at.button(key='run').disabled
    at.button(key='confirm').click().run();at.button(key='run').click().run()
    assert not at.exception
    assert ctl.result.request.parameters['beam_depth_mm'].value==600
    assert ctl.completed_runs==2


def test_web_mechanism_experiment_is_explicit_and_not_repeated_on_render():
    at=app()
    at.radio(key='nav').set_value('对照实验').run()
    at.button(key='run_mechanism').click().run()
    assert not at.exception
    record=at.session_state['mechanism_record'];stamp=record['completed_at_utc']
    assert len(record['rows'])==180 and all(r['equal_to_full'] for r in record['rows'])
    at.run()
    assert at.session_state['mechanism_record']['completed_at_utc']==stamp


def test_missing_parameters_are_located_in_their_group_and_cannot_confirm():
    at=app()
    ctl=at.session_state['workbench']
    request=ctl.draft.request.model_copy(deep=True)
    request.parameters.pop('live_load_kn_m')
    ctl.load(request,'缺项案例')
    at.run()
    assert not at.exception
    assert any(tab.label=='荷载 · 缺1项' for tab in at.tabs)
    assert any('本组必填缺项：活载' in item.value for item in at.warning)
    assert at.button(key='confirm').disabled and at.button(key='run').disabled
    assert ctl.completed_runs==0


def test_batch_filter_and_consultation_disclosure_do_not_execute_again():
    at=app('已有梁独立验算')
    at.button(key='confirm').click().run();at.button(key='run').click().run()
    ctl=at.session_state['workbench']
    at.radio(key='nav').set_value('Agent 与动态规划').run()
    count=len(ctl.calls)
    at.selectbox(key='agent_batch').select('all').run()
    at.selectbox(key='agent_batch').select(1).run()
    assert not at.exception and len(ctl.calls)==count and ctl.completed_runs==1
    at.radio(key='nav').set_value('专家咨询').run()
    assert at.button(key='ask_expert').disabled
    at.text_area(key='expert_query').set_value('梁高改为600mm').run()
    at.button(key='ask_expert').click().run()
    assert not at.exception
    assert any(item.label.startswith('查看依据') for item in at.expander)
    count=len(ctl.calls)
    at.run()
    assert len(ctl.calls)==count and ctl.completed_runs==1


def test_material_selection_requires_validation_and_does_not_fill_missing_grade():
    at=app()
    ctl=at.session_state['workbench']
    request=ctl.draft.request.model_copy(deep=True)
    request.parameters.pop('concrete_grade')
    ctl.load(request,'未指定混凝土等级')
    at.run()
    generation=ctl.editor_generation
    assert at.selectbox(key=f'enum_concrete_grade_{generation}').value is None
    assert at.button(key='confirm').disabled and at.button(key='run').disabled
    at.button(key='validate').click().run()
    assert 'concrete_grade' in ctl.draft.missing_parameters
    assert at.button(key='confirm').disabled and ctl.completed_runs==0
    generation=ctl.editor_generation
    at.selectbox(key=f'enum_concrete_grade_{generation}').select('C40').run()
    at.button(key='validate').click().run()
    assert not at.exception
    assert ctl.draft.request.parameters['concrete_grade'].value=='C40'
    assert ctl.stage=='validated' and not ctl.draft.confirmed


def test_report_feedback_search_selection_and_calculation_steps():
    import runpy
    from engi_agent.ui.service import WorkbenchSession
    make=runpy.run_path(str(ROOT/'examples/reproduce_report_feedback.py'))['report_request']
    r=make();r.auto_redesign=True;r.solution_count=2;r.search_diameters_mm=[20,22];r.max_iterations=6
    ctl=WorkbenchSession();ctl.load(r,'用户计算书复现')
    at=AppTest.from_file(str(ROOT/'streamlit_app.py'),default_timeout=30).run()
    at.session_state['workbench']=ctl;at.run()
    at.button(key='confirm').click().run();at.button(key='run').click().run()
    assert not at.exception
    assert ctl.result.candidate['bar_diameter_mm']==22
    calls=len(ctl.calls)
    at.selectbox(key='verified_alternative').select(2).run()
    at.button(key='select_alternative').click().run()
    assert not at.exception and ctl.result.candidate['bar_diameter_mm']==20
    assert len(ctl.calls)==calls+1 and ctl.completed_runs==1
    at.radio(key='nav').set_value('计算与规范复核').run()
    assert not at.exception
    assert any('分步计算' in element.value for element in at.markdown)
    assert any('代入：' in element.value for element in at.markdown)


def test_review_is_latex_and_formal_references_without_raw_code():
    at=app('已有梁独立验算')
    at.button(key='confirm').click().run();at.button(key='run').click().run()
    at.radio(key='nav').set_value('计算与规范复核').run()
    assert not at.exception and len(at.get('latex'))>10
    assert not at.get('json') and not at.get('code')
    visible=' '.join(item.value for item in at.markdown)+' '.join(item.value for item in at.caption)
    assert 'docs/' not in visible and 'cn-rc-' not in visible
    assert '混凝土结构设计标准' in visible


def test_unsized_search_scope_is_visible_before_confirmation_and_shortlist_after_run():
    import runpy
    from engi_agent.ui.service import WorkbenchSession
    make=runpy.run_path(str(ROOT/'examples/reproduce_report_feedback.py'))['report_request']
    r=make();r.parameters.pop('beam_width_mm');r.parameters.pop('beam_depth_mm')
    r.max_iterations=6;r.solution_count=3;r.search_diameters_mm=[20,22]
    ctl=WorkbenchSession();ctl.load(r,'截面留空设计')
    at=AppTest.from_file(str(ROOT/'streamlit_app.py'),default_timeout=30).run()
    at.session_state['workbench']=ctl;at.run()
    assert any('250–450' in element.value and '500–800' in element.value for element in at.info)
    at.button(key='confirm').click().run();at.button(key='run').click().run()
    assert not at.exception and ctl.result.evaluation.status=='pass'
    assert len(ctl.result.design_alternatives)==3
    assert any('剔除支配方案' in element.value for element in at.caption)
    before=ctl.result.design_revision
    selected=ctl.result.design_alternatives[-1]['revision']
    at.selectbox(key='verified_alternative').select(selected).run()
    at.button(key='select_alternative').click().run()
    assert not at.exception and ctl.result.design_revision==selected!=before


def test_expert_suggestion_fills_without_submitting_and_renders_legacy_math():
    at=app('已有梁独立验算')
    at.button(key='confirm').click().run();at.button(key='run').click().run()
    at.radio(key='nav').set_value('专家咨询').run()
    ctl=at.session_state['workbench'];calls=len(ctl.calls);runs=ctl.completed_runs
    suggested=at.button(key='expert_suggestion_0').label
    at.button(key='expert_suggestion_0').click().run()
    assert at.text_area(key='expert_query').value==suggested
    assert len(ctl.calls)==calls and ctl.completed_runs==runs and not ctl.consultations
    assert not any('离线咨询仅支持' in item.value or 'DeepSeek 会结合' in item.value for item in at.caption)
    reply=ctl.ask_expert('当前参数是多少')
    ctl.consultations[-1]['answer']=r'系数 \(\psi\) 与刚度有关。'+'\n'+r'\[B_s=\frac{E_s A_s h_0^2}{1.15\psi+0.2}\]'
    at.run()
    assert not at.exception and len(at.get('latex'))>=1
    assert len(ctl.calls)==calls+1 and ctl.completed_runs==runs
