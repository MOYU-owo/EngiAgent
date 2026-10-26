"""Streamlit widget flows; no hosted model calls. Run when ui extras are installed."""
import json
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
    for page in ('计算与规范复核','Agent 与动态规划','对照实验','设计工作台'):
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
    at.session_state[f'editor_几何_{g}']={'edited_rows':{5:{'输入值':'600'}},'added_rows':[],'deleted_rows':[]}
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
