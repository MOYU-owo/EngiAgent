"""Run and export the same-kernel mechanism experiment without hosted requests."""
import json
from pathlib import Path
from engi_agent.engineering.experiments import run_mechanism_experiment, experiment_markdown


if __name__=='__main__':
    record=run_mechanism_experiment()
    folder=Path('outputs/research');folder.mkdir(parents=True,exist_ok=True)
    (folder/'mechanism_ablation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    (folder/'mechanism_ablation.md').write_text(experiment_markdown(record),encoding='utf-8')
    print(json.dumps({'cases':record['case_count'],'summary':record['summary']},ensure_ascii=True))
