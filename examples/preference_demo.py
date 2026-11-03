"""Small automatic demo using real CN calculations and explicitly synthetic votes."""
import json
import os
from pathlib import Path
from engi_agent.ui.service import WorkbenchSession,load_case
from engi_agent.ui.preference_panel import simulate_evaluations
from engi_agent.engineering.preferences import PreferenceStore


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,default=Path('outputs/preference_demo_v1'))
    out=parser.parse_args().output_dir;out.mkdir(parents=True,exist_ok=True)
    os.environ['ENGIAGENT_PREFERENCE_DIR']=str(out/'profiles')
    ctl=WorkbenchSession();ctl.load(load_case('截面与配筋联合设计'),'偏好演示');ctl.confirm();ctl.run('program')
    before=PreferenceStore('simulated').load()[0]
    after=simulate_evaluations(ctl.result)
    comparison=ctl.compare_preferences('simulated')
    (out/'comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2),encoding='utf-8')
    summary=dict(source='simulated',before=before.model_dump(),after=after.model_dump(),
        metrics={k:v['metrics'] for k,v in comparison['results'].items()},
        sequence={k:[(h['candidate'].get('beam_width_mm'),h['candidate'].get('beam_depth_mm'),h['candidate'].get('bar_count'),h['candidate'].get('bar_diameter_mm')) for h in v['state']['revisions']] for k,v in comparison['results'].items()})
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=True,indent=2))


if __name__=='__main__':main()
