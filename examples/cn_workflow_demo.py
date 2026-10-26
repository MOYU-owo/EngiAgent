"""Offline acceptance demonstration: five scenarios plus selective recomputation."""
import json
from pathlib import Path
from engi_agent.engineering.schema import TaskRequest
from engi_agent.engineering.workflow import prepare,confirm,run_engineering
from engi_agent.engineering.cn_workflow import revise
from engi_agent.engineering.roles import FixtureRoles
from engi_agent.engineering.reporting import markdown_report


def main():
    directory=Path('outputs/cn_validation'); directory.mkdir(parents=True,exist_ok=True)
    records=[]; existing=None
    for name in ('cn_design','cn_existing','cn_flexure_only','cn_redesign','cn_no_solution'):
        request=TaskRequest.model_validate_json(Path(f'examples/engineering/{name}.json').read_text(encoding='utf-8'))
        state=run_engineering(confirm(prepare(request)),FixtureRoles(request))
        want='fail' if name=='cn_no_solution' else 'pass'
        assert state.evaluation.status==want,(name,state.errors)
        (directory/f'{name}.json').write_text(state.model_dump_json(indent=2),encoding='utf-8')
        (directory/f'{name}.md').write_text(markdown_report(state,f'{name}.json'),encoding='utf-8')
        records.append(dict(case=name,status=state.evaluation.status,iterations=len(state.revisions),
                            checks=state.evaluation.checks,candidate=state.candidate))
        if name=='cn_existing':existing=state
    pending=revise(existing,{'beam_depth_mm':{'value':600,'unit':'mm'}})
    changed=run_engineering(confirm(pending),FixtureRoles(pending.request))
    fresh=run_engineering(confirm(prepare(pending.request)),FixtureRoles(pending.request))
    for key,result in changed.tool_results.items(): assert result.outputs==fresh.tool_results[key].outputs
    (directory/'cn_height_revision.json').write_text(changed.model_dump_json(indent=2),encoding='utf-8')
    (directory/'cn_height_revision.md').write_text(markdown_report(changed,'cn_height_revision.json'),encoding='utf-8')
    records.append(dict(case='cn_height_revision',status=changed.evaluation.status,full_recompute_equal=True,
                        trace=changed.plan_trace))
    (directory/'summary.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    for r in records: print(r['case'],r['status'])
    print(directory.resolve())


if __name__=='__main__':main()
