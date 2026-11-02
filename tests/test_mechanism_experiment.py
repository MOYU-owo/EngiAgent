"""The ablation compares identical requested outputs and reports only measured work."""
from engi_agent.engineering.experiments import run_mechanism_experiment, experiment_markdown
from engi_agent.engineering.roles import ProgramRoles
from engi_agent.ui.service import WorkbenchSession,load_case


def test_twenty_cases_three_groups_have_identical_requested_outputs():
    record=run_mechanism_experiment(repeats=1)
    assert record['case_count']==20 and len(record['rows'])==60
    assert all(r['equal_to_full'] and r['model_calls']==0 for r in record['rows'])
    rows={r['group']:r for r in record['rows'] if r['case_id']=='excluded_all_height'}
    assert rows['full']['executed']==11 and rows['dag_cache']['executed']==10
    rows={r['group']:r for r in record['rows'] if r['case_id']=='excluded_all_crack_limit'}
    assert rows['dag_cache']['reused']==10
    rows={r['group']:r for r in record['rows'] if r['case_id']=='included_flexure_unchanged'}
    assert rows['full']['executed']==11 and rows['dag']['executed']==7
    assert rows['dag_cache']['executed']==0
    assert all(r['all_equal_to_full'] for r in record['summary'])
    assert record['source_hashes'] and '不包含模型请求' in experiment_markdown(record)


def test_program_mode_runs_real_tools_without_model_roles():
    s=WorkbenchSession();s.load(load_case('完整新方案设计'),'program');s.confirm();s.run('program')
    assert s.result.evaluation.status=='pass'
    assert all(c.mode=='program' for c in s.calls if c.role!='Dispatcher')
    assert ProgramRoles().plan('Design',{'required_steps':['materials']}).steps==['materials']
