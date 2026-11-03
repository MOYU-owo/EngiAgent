from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]


def test_existing_page_pair_voting_simulation_and_search_comparison(tmp_path,monkeypatch):
    monkeypatch.setenv('ENGIAGENT_PREFERENCE_DIR',str(tmp_path/'profiles'))
    at=AppTest.from_file(str(ROOT/'streamlit_app.py'),default_timeout=30).run()
    at.selectbox(key='case_selector').select('截面与配筋联合设计').run()
    at.button(key='load_case').click().run();at.button(key='confirm').click().run();at.button(key='run').click().run()
    assert not at.exception
    at.button(key='pref_choose_a').click().run()
    from engi_agent.engineering.preferences import PreferenceStore
    assert PreferenceStore('real').load()[0].version==1
    at.radio(key='pref_source').set_value('simulated').run()
    at.button(key='pref_simulate').click().run()
    assert not at.exception and PreferenceStore('simulated').load()[0].version==20
    at.button(key='pref_compare').click().run()
    assert not at.exception
    comparison=at.session_state['workbench'].preference_comparison
    assert comparison['source']=='simulated' and len(comparison['results'])==2
    assert PreferenceStore('real').load()[0].version==1
    at.checkbox(key='pref_enabled').check().run();at.button(key='pref_apply').click().run()
    assert not at.exception and at.session_state['workbench'].stage=='validated'
    assert at.session_state['workbench'].draft.request.preference_guidance
