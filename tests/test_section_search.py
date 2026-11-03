"""Joint section/reinforcement search against the user's unsized report case."""
import math
import runpy
from pathlib import Path

import pytest

from engi_agent.engineering.cn_schema import ParameterValue, CNParameters
from engi_agent.engineering.cn_workflow import prepare, confirm, run_engineering
from engi_agent.engineering.cn_presentation import parameter_rows, confirmation_text
from engi_agent.engineering.design_search import shortlist
from engi_agent.engineering.roles import ProgramRoles
from engi_agent.ui.service import WorkbenchSession

make = runpy.run_path(str(Path(__file__).resolve().parents[1]/'examples/reproduce_report_feedback.py'))['report_request']


def request(rounds=12):
    r = make()
    r.parameters.pop('beam_width_mm'); r.parameters.pop('beam_depth_mm')
    r.auto_redesign = True; r.max_iterations = rounds
    r.search_diameters_mm = [20,22]; r.solution_count = 3
    return r


def setp(r, key, value):
    r.parameters[key] = ParameterValue(value=value, unit='mm')


def run(r):
    return run_engineering(confirm(prepare(r)), ProgramRoles())


def test_actual_report_inputs_repair_within_original_six_round_budget():
    r = request(6); s = run(r)
    assert s.evaluation.status == 'pass' and len(s.revisions) == 6
    assert len(s.design_alternatives) == 3
    assert s.revisions[0]['candidate']['beam_depth_mm'] == 500
    assert s.revisions[0]['evaluation']['checks']['deflection'] is False
    assert s.revisions[1]['candidate']['beam_depth_mm'] == 550
    assert s.candidate['beam_depth_mm'] == 550
    assert s.candidate['bar_count'] == 3 and s.candidate['bar_diameter_mm'] == 22
    # A spacing failure is followed by widening, not a sixth/seventh bar.
    layout = s.revisions[4]
    assert not layout['evaluation']['checks']['detailing']
    assert s.revisions[5]['candidate']['beam_width_mm'] > layout['candidate']['beam_width_mm']
    assert s.revisions[5]['candidate']['bar_count'] == layout['candidate']['bar_count']
    assert all(all(a['checks'].values()) for a in s.design_alternatives)
    assert s.request.parameters == confirm(prepare(r)).request.parameters


@pytest.mark.parametrize('fixed, value, other', [
    ('beam_width_mm',250,'beam_depth_mm'), ('beam_depth_mm',500,'beam_width_mm')])
def test_only_the_unspecified_dimension_may_change(fixed,value,other):
    r = request(); setp(r, fixed, value); s = run(r)
    assert s.evaluation.status == 'pass'
    assert all(h['candidate'].get(fixed) == value for h in s.revisions if h['candidate'])
    assert any(h['candidate'].get(other) != s.revisions[0]['candidate'][other] for h in s.revisions if h['candidate'])


def test_explicit_upper_bounds_are_not_relaxed_when_infeasible():
    r = request(10); setp(r,'max_width_mm',250); setp(r,'max_depth_mm',500)
    s = run(r)
    assert s.evaluation.status == 'fail' and not s.design_alternatives
    assert len(s.revisions) <= 10 and s.search_stop_reason and s.errors
    assert all(h['candidate']['beam_width_mm'] <= 250 and h['candidate']['beam_depth_mm'] <= 500
               for h in s.revisions if h['candidate'])
    assert s.request.parameters['crack_limit_mm'].value == .3
    assert s.request.parameters['cover_mm'].value == 35


def test_initial_section_can_be_below_experience_size_when_user_sets_lower_upper_bound():
    r = request(1); setp(r, 'max_depth_mm', 475)
    s = run(r)
    assert s.revisions[0]['parameters']['beam_depth_mm'] == 475
    assert s.design_search['domain']['beam_depth_mm']['bound_source'] == '用户上限'


def test_resizing_recomputes_selfweight_analysis_and_matches_fresh_existing_check():
    r = request(6); s = run(r)
    first, taller = s.revisions[:2]
    loads = lambda h: h['tools']['evaluation.load_combination']['outputs']
    assert loads(taller)['added_self_weight_kn_m'] > loads(first)['added_self_weight_kn_m']
    assert loads(taller)['ultimate_load_kn_m'] > loads(first)['ultimate_load_kn_m']
    assert any(t['tool']=='materials' and t['action']=='reuse' for t in taller['trace'])
    assert any(t['tool']=='beam_analysis' and t['action']=='invalidate_execute' for t in taller['trace'])
    check = r.model_copy(deep=True); check.task_type='evaluate_existing'; check.auto_redesign=False
    for k,v in s.candidate.items():
        if k in CNParameters.model_fields:
            check.parameters[k] = ParameterValue(value=v,unit='mm' if k.endswith('_mm') else None)
    fresh = run(check)
    for name in ('flexural_check','shear_check','detailing_check','crack_check','deflection_check'):
        assert s.tool_results['evaluation.'+name].outputs == fresh.tool_results['evaluation.'+name].outputs


def test_shortlist_filters_duplicates_and_dominance_and_selection_keeps_evidence():
    r = request(); session=WorkbenchSession();session.load(r,'unsized report');session.confirm();session.run('program')
    s = session.result; stats=s.design_search['filter']
    assert stats['passed'] > stats['displayed'] == 3
    assert stats['dominated'] >= 1
    duplicated = [*s.revisions, next(h for h in s.revisions if h['evaluation']['status']=='pass')]
    filtered, summary = shortlist(duplicated,6000,3)
    assert summary['duplicates'] == 1 and len(filtered) == 3
    assert [a['revision'] for a in filtered] == [a['revision'] for a in s.design_alternatives]
    selected = s.design_alternatives[-1]; calls=len(session.calls)
    session.select_design_alternative(selected['revision'])
    assert session.result.candidate == selected['candidate']
    assert len(session.calls) == calls+1 and session.completed_runs == 1
    revision=next(h for h in s.revisions if h['revision']==selected['revision'])
    assert {k:v.model_dump() for k,v in session.result.tool_results.items()} == revision['tools']


def test_report_distinguishes_initial_diameter_from_actual_selected_value():
    s=run(request(6))
    row=next(row for row in parameter_rows(s) if row[2]=='纵筋直径')
    assert row[3]=='20 mm' and row[4]=='22 mm' and '工具选用' in row[5]
    before=confirmation_text(prepare(request()))
    assert '250–450' in before and '500–800' in before and '不是规范限值' in before


def test_nonrepairable_anchor_conditions_do_not_trigger_unbounded_bar_increases():
    r=request(40);setp(r,'end_anchor_length_mm',200)
    s=run(r)
    assert s.evaluation.status == 'fail' and not s.design_alternatives
    assert len(s.revisions) < 40
    assert all(h['parameters']['end_anchor_length_mm'] == 200 for h in s.revisions)
