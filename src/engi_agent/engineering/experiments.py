"""Reproducible same-kernel ablation. This is not external engineering validation."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import platform
from pathlib import Path
from statistics import median
from time import perf_counter

from .cn_schema import TaskRequest, ParameterValue
from .roles import ProgramRoles
from .cn_workflow import prepare, confirm, run_engineering
from .cn_workflow import ALL_TARGETS, revise
from .dependency_graph import TARGET_TOOLS

ROOT=Path(__file__).resolve().parents[3]
GROUPS=('full','dag','dag_cache')


def _run(request):
    return run_engineering(confirm(prepare(request)),ProgramRoles())


def run_mechanism_experiment(repeats=3):
    if isinstance(repeats,bool) or not isinstance(repeats,int) or not 1<=repeats<=10:
        raise ValueError('重复次数应为1至10的整数')
    rows=[]
    base=TaskRequest.model_validate_json((ROOT/'examples/engineering/cn_existing.json').read_text(encoding='utf-8'))
    patches={'height':{'beam_depth_mm':{'value':600,'unit':'mm'}},
             'live_load':{'live_load_kn_m':{'value':6,'unit':'kN/m'}},
             'crack_limit':{'crack_limit_mm':{'value':.25,'unit':'mm'}},
             'bars':{'bar_count':{'value':4,'unit':None}}, 'unchanged':{}}
    for weight_mode in ('included','excluded'):
        for targets in (ALL_TARGETS,['flexure']):
            request=base.model_copy(deep=True)
            request.parameters['self_weight_mode']=ParameterValue(value=weight_mode)
            request.targets=targets.copy()
            full_request=request.model_copy(deep=True);full_request.targets=ALL_TARGETS.copy()
            initial={'full':_run(full_request),'dag':_run(request),'dag_cache':_run(request)}
            for kind,patch in patches.items():
                case_id=weight_mode+'_'+('all' if len(targets)>1 else 'flexure')+'_'+kind
                expected=None
                for repeat in range(repeats):
                    # Rotate group order to reduce a fixed first/last-run advantage.
                    for group in GROUPS[repeat%3:]+GROUPS[:repeat%3]:
                        started=perf_counter()
                        pending=revise(initial[group],patch)
                        if group!='dag_cache':pending.cache={}
                        result=run_engineering(confirm(pending),ProgramRoles())
                        elapsed=perf_counter()-started
                        outputs={t:result.tool_results['evaluation.'+TARGET_TOOLS[t]].outputs for t in targets}
                        if expected is None:expected=outputs
                        equal=outputs==expected
                        if not equal:raise AssertionError('局部/全量输出不一致：'+case_id)
                        counts=Counter(t['action'] for t in result.plan_trace)
                        rows.append({'case_id':case_id,'group':group,'repeat':repeat+1,
                            'requested_targets':targets.copy(),'delta':patch,'outputs':outputs,
                            'input_hash':hashlib.sha256(request.model_dump_json().encode()).hexdigest(),
                            'equal_to_full':equal,'status':result.evaluation.status,
                            'requested_checks':{t:outputs[t].get('pass') for t in targets},
                            'executed':counts['execute']+counts['invalidate_execute'],
                            'reused':counts['reuse'],'blocked':counts['blocked'],
                            'elapsed_wall_seconds':elapsed,'model_calls':0})
    summary=[]
    for group in GROUPS:
        values=[r for r in rows if r['group']==group]
        summary.append({'group':group,'runs':len(values),'cases':len({r['case_id'] for r in values}),
            'all_equal_to_full':all(r['equal_to_full'] for r in values),
            'executed_total':sum(r['executed'] for r in values),'reused_total':sum(r['reused'] for r in values),
            'median_wall_seconds':median(r['elapsed_wall_seconds'] for r in values),
            'min_wall_seconds':min(r['elapsed_wall_seconds'] for r in values),
            'max_wall_seconds':max(r['elapsed_wall_seconds'] for r in values)})
    sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
             for p in [Path(__file__), *(Path(__file__).parent/name for name in
                        ('cn_tools.py','cn_workflow.py','dependency_graph.py','cn_schema.py','roles.py')),
                        ROOT/'examples/engineering/cn_existing.json']}
    return {'schema_version':1,'kind':'same_kernel_mechanism_ablation','completed_at_utc':datetime.now(timezone.utc).isoformat(),
            'python':platform.python_version(),'platform':platform.platform(),'source_hashes':sources,
            'repeats':repeats,'case_count':20,'summary':summary,'rows':rows,
            'limitations':['无模型网络请求、无人工作业时间、无外部工程真值',
                          '同内核、20种模板派生的目标/修改组合，不代表20个独立工程基准',
                          '初始结果已预热，计时包含修订、确认、编排与工具，不含初次启动',
                          '纯抗弯组只比较请求项；全量基线额外检查不用于推断局部任务全面通过',
                          '结果仅证明被测场景一致性和本机执行代价，不证明模型或多Agent优越性']}


def experiment_markdown(record):
    lines=['# 工程依赖机制对照实测','',f"UTC：{record['completed_at_utc']}",'',
           f"20种组合，每组重复{record['repeats']}次；不包含模型请求和人工时间。",'',
           '|组别|运行数|实际执行节点合计|复用合计|耗时中位数/s|输出一致|',
           '|---|---:|---:|---:|---:|---|']
    for r in record['summary']:
        lines.append(f"|{r['group']}|{r['runs']}|{r['executed_total']}|{r['reused_total']}|{r['median_wall_seconds']:.6f}|{r['all_equal_to_full']}|")
    return '\n'.join(lines+['','full=全量无缓存；dag=按目标无缓存；dag_cache=按目标及有效缓存。','']+
                      ['- '+s for s in record['limitations']])+ '\n'
