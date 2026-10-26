"""Confirmed-input workflow, DAG execution/cache and bounded design revisions."""
import hashlib
import json
from pydantic import TypeAdapter
from langgraph.graph import StateGraph, START, END
from .schema import (EngineeringState, EvaluationResult, ParameterValue, ProgressEvent,
                     TaskRequest, ToolResult, FACTORS, parameter_python)
from .cn_schema import CNParameters, CNProfile, CN_UNITS, CN_INTEGERS, cn_required
from .dependency_graph import SPECS, TARGET_TOOLS, build_plan, dependencies
from . import cn_tools
from .tools import EngineeringFailure
from .cn_outputs import validate_output

ALL_TARGETS = ['flexure', 'shear', 'detailing', 'crack', 'deflection']
REFS={
    'materials':['GB/T50010 4.1、4.2（2024修订）','GB55008 2.0.2、表3.2.1'],
    'section_sizing':['项目经验初选L/12、b=0.5h；非规范验算'],
    'section_geometry':['GB/T50010 6.2 几何定义；9.2.1'],
    'load_combination':['GB55001 3.1.13；GB50009 5.1、附录A'],
    'beam_analysis':['结构力学：简支均布荷载；GB/T50010 6.3.2支座边缘检查'],
    'demand':['已确认设计内力/承载力荷载组合；来源独立列出'],
    'flexural_design':['GB/T50010 6.2.1、6.2.6—6.2.10；GB55008 4.4.6'],
    'flexural_check':['GB/T50010 6.2.1、6.2.6—6.2.10；GB55008 4.4.6'],
    'shear_design':['GB/T50010 6.3.1、6.3.4、9.2.9'],
    'shear_check':['GB/T50010 6.3.1、6.3.4、9.2.9'],
    'detailing_check':['GB/T50010 8.2、8.3、9.2.1、9.2.6、9.2.9、9.2.13；GB55008 2.0.10、4.4.5'],
    'crack_check':['GB/T50010 3.4.2、7.1.1、7.1.2、7.1.4-3'],
    'deflection_check':['GB/T50010 表3.4.3、7.2.1—7.2.3、7.2.5'],
}


def normalize_cn(request):
    request = TaskRequest.model_validate(request.model_dump()).model_copy(deep=True)
    extra_units = {'kN·m': {'kN·m': 1, 'kN*m': 1, 'N·mm': 1e-6}, 'kN': {'kN': 1, 'N': .001}}
    for key, item in request.parameters.items():
        if key not in CN_UNITS: raise ValueError(f'中国规范模式未知参数：{key}')
        item.raw_value = item.value if item.raw_value is None else item.raw_value
        item.raw_unit = item.unit if item.raw_unit is None else item.raw_unit
        if key=='safety_class' and item.value=='二级': item.value='2'
        if key=='environment_class' and item.value in ('一类','Ⅰ'): item.value='I'
        unit = CN_UNITS[key]
        if isinstance(item.value, bool): raise ValueError(f'{key}不能使用布尔值')
        if unit:
            factors = extra_units.get(unit, FACTORS.get(unit))
            if item.unit not in factors: raise ValueError(f'{key}单位不匹配，应为{unit}')
            item.value = float(item.value)*factors[item.unit]; item.unit = unit
        elif item.unit not in (None, '', '1'):
            raise ValueError(f'{key}为无量纲/枚举参数')
        if key in CN_INTEGERS:
            if float(item.value) != int(float(item.value)): raise ValueError(f'{key}必须为整数')
            item.value = str(int(float(item.value)))
        TypeAdapter(CNParameters.model_fields[key].rebuild_annotation()).validate_python(parameter_python(key, item))
    if request.task_type == 'new_design': request.targets = ALL_TARGETS.copy()
    if set(request.targets)-set(ALL_TARGETS): raise ValueError('中国规范模式不使用教学弹性挠度目标，请用deflection')
    return request


def prepare_cn(request, profile=None):
    if profile is not None and not isinstance(profile,CNProfile):
        raise ValueError('中国规范任务不能使用教学计算配置')
    r = normalize_cn(request)
    return EngineeringState(request=r, profile=profile or CNProfile(),
                            missing_parameters=sorted(cn_required(r)-r.parameters.keys()))


def confirm_cn(state):
    from .workflow import stamp
    fresh = prepare_cn(state.request, state.profile)
    if fresh.missing_parameters: raise ValueError('缺少参数：'+','.join(fresh.missing_parameters))
    if fresh.request.task_type == 'new_design' and any(k in fresh.request.parameters for k in ('design_moment_kn_m', 'design_shear_kn')):
        raise ValueError('新设计须由确认的恒活载计算内力；直接内力仅用于已有梁验算')
    if fresh.request.auto_redesign and fresh.request.task_type != 'new_design':
        raise ValueError('已有梁独立验算不会自动改变用户配筋，请创建新设计任务')
    for v in fresh.request.parameters.values(): v.confirmed = True
    fresh.confirmed = True; fresh.confirmation_hash = stamp(fresh)
    # Preserve earlier trace/cache, but never preserve an earlier pass conclusion.
    fresh.cache = state.cache.copy()
    fresh.revisions = state.revisions.copy()
    fresh.design_revision = state.design_revision
    fresh.revision_reason = state.revision_reason
    return fresh


def revise(state, changes, *, targets=None):
    """Create an unconfirmed revision; caller must confirm again before execution."""
    if state.request.code != 'cn-2024': raise ValueError('局部重算接口当前仅支持中国规范模式')
    revised = state.model_copy(deep=True)
    for key, raw in changes.items():
        item = raw if isinstance(raw, ParameterValue) else ParameterValue.model_validate(raw)
        item = item.model_copy(deep=True)
        item.confirmed = False; item.raw_value = None; item.raw_unit = None
        item.revision = state.design_revision+1
        revised.request.parameters[key] = item
    if targets is not None: revised.request.targets = targets
    revised.confirmed = False; revised.confirmation_hash = None
    revised.design_revision += 1
    revised.revision_reason='用户修改：'+','.join(changes) if changes else '重新核对原参数'
    revised.cache.update(state.tool_results)
    return confirm_preparation(revised)


def confirm_preparation(state):
    fresh = prepare_cn(state.request, state.profile)
    fresh.cache, fresh.revisions = state.cache, state.revisions
    fresh.design_revision = state.design_revision
    fresh.revision_reason = state.revision_reason
    return fresh


def _run_plan(state, params, phase, roles, on_event):
    from .workflow import emit_progress, invoke_role
    design = phase == 'design'
    targets = ['flexure', 'shear'] if design else state.request.targets
    plan = build_plan(targets, params, design=design)
    if not invoke_role(state, roles, 'Design' if design else 'Evaluation', plan, on_event): return False
    outputs = {}; good = True
    for i, name in enumerate(plan, 1):
        key = f'{phase}.{name}'; state.execution_plan.append(key)
        deps = dependencies(name, params, targets)
        absent = [d for d in deps if d not in outputs]
        selected = {k: params.get(k) for k in SPECS[name].fields}
        upstream = {d: outputs[d] for d in deps if d in outputs}
        inputs = {'parameters': selected, 'upstream': upstream, 'formula_version': SPECS[name].version,
                  'profile': state.profile.model_dump()}
        digest = hashlib.sha256(json.dumps(inputs, sort_keys=True, allow_nan=False).encode()).hexdigest()
        cached = state.cache.get(key)
        action = 'execute'
        if absent:
            result = ToolResult(tool=name, status='blocked', inputs_hash=digest, inputs=inputs,
                                errors=['上游无有效输出：'+','.join(absent)])
            action = 'blocked'; good = False
        elif cached and cached.status == 'success' and cached.inputs_hash == digest:
            result = cached.model_copy(deep=True); action = 'reuse'
        else:
            result = ToolResult(tool=name, status='success', inputs_hash=digest, inputs=inputs)
            if cached: action = 'invalidate_execute'
            try:
                # Functions receive only declared fields. Hidden dependencies fail closed.
                actual = {k: v for k, v in selected.items() if v is not None}
                result.outputs = validate_output(name,cn_tools.REGISTRY[name](actual, upstream))
                json.dumps(result.outputs, allow_nan=False)
                if 'pass' in result.outputs and type(result.outputs['pass']) is not bool:
                    raise TypeError('验算判定不是布尔值')
            except EngineeringFailure as exc:
                result.status = 'failed'; result.errors = [str(exc)]
                result.outputs = {'engineering_failure': True, 'pass': False}; good = False
            except Exception as exc:
                result.status = 'failed'; result.errors = [f'{type(exc).__name__}: 工具执行异常']; good = False
        result.formula_version = SPECS[name].version
        result.code_refs = REFS[name]+['docs/rc_beam_cn_design_spec.md','docs/rc_beam_cn_formula_review.md']
        result.revision = state.design_revision
        state.tool_results[key] = result
        state.plan_trace.append(dict(revision=state.design_revision, phase=phase, tool=name, action=action,
                                     reason='输入及版本一致' if action=='reuse' else '依赖输入变化' if action=='invalidate_execute' else
                                     '上游失败' if action=='blocked' else '首次需要该计算'))
        emit_progress(state, on_event, ProgressEvent(phase=phase, kind='tool', name=name, status=result.status,
                      step=i, total_steps=len(plan), outputs=result.outputs, errors=result.errors))
        if result.status == 'success':
            outputs[name] = result.outputs
            state.cache[key] = result.model_copy(deep=True)
    return good


def run_cn(state, roles, on_event=None):
    from .workflow import stamp, error_state
    state = state.model_copy(deep=True)
    def reject(message):
        state.tool_results={};state.candidate={};state.execution_plan=[];state.plan_trace=[]
        state.evaluation=EvaluationResult(status='error')
        return error_state(state,message)
    if not state.confirmed or not all(v.confirmed for v in state.request.parameters.values()) or state.confirmation_hash != stamp(state):
        return reject('参数或假设未确认，拒绝计算')
    if not isinstance(state.profile, CNProfile): return reject('中国规范任务与计算配置不匹配')
    base = {k: parameter_python(k,v) for k,v in state.request.parameters.items()}
    context = {'parameters': base.copy(), 'minimum_bar_count': 2, 'iteration': 0,'reason':state.revision_reason}
    state.errors = []; state.tool_results = {}; state.execution_plan = []; state.plan_trace = []
    state.evaluation = EvaluationResult()

    def design(data):
        s = data['state']; p = context['parameters'].copy()
        p['minimum_bar_count'] = context['minimum_bar_count']
        s.candidate = {}
        if _run_plan(s, p, 'design', roles, on_event):
            g = s.tool_results['design.section_sizing'].outputs
            f = s.tool_results['design.flexural_design'].outputs
            t = s.tool_results['design.shear_design'].outputs
            s.candidate = {**{k:g[k] for k in ('beam_width_mm','beam_depth_mm')},
                           'bar_count':f['bar_count'], 'bar_diameter_mm':p['bar_diameter_mm'],
                           'stirrup_diameter_mm':p['stirrup_diameter_mm'], 'stirrup_legs':p['stirrup_legs'],
                           'end_anchor_stirrup_spacing_mm':p['end_anchor_stirrup_spacing_mm'],
                           'As_mm2':f['As_mm2'], 'stirrup_spacing_mm':t['stirrup_spacing_mm'], 'status':'draft'}
        return {'state':s}

    def evaluate(data):
        s = data['state']; context['iteration'] += 1
        if s.errors:
            s.evaluation = EvaluationResult(status='error')
        elif s.request.task_type == 'new_design' and not s.candidate:
            results = [r for k,r in s.tool_results.items() if k.startswith('design.')]
            status = 'fail' if any(r.outputs.get('engineering_failure') for r in results) else 'error'
            s.evaluation = EvaluationResult(status=status)
        else:
            p = {**context['parameters'], **{k:v for k,v in s.candidate.items() if k in CNParameters.model_fields}}
            _run_plan(s, p, 'evaluation', roles, on_event)
            relevant = [s.tool_results.get('evaluation.'+TARGET_TOOLS[t]) for t in s.request.targets]
            errors = s.errors or any(r is None or r.status != 'success' for r in relevant)
            checks = {t: bool(r and r.status=='success' and r.outputs.get('pass') is True)
                      for t,r in zip(s.request.targets,relevant)}
            engineering = any(r and r.outputs.get('engineering_failure') for r in relevant)
            status = 'error' if errors and not engineering else 'pass' if all(checks.values()) else 'fail'
            omitted = [f'本次未请求：{t}' for t in ALL_TARGETS if t not in s.request.targets]
            s.evaluation = EvaluationResult(status=status, checks=checks,
                code_status='已核验支持范围内项目' if status != 'error' else '未完成',
                overall_status='incomplete',
                unimplemented=omitted+['实际支承约束、节点详图、防火及完整耐久性审查需工程师复核',
                                      '首箍、封闭箍弯钩和腰筋拉结需在施工图落实；当前输出要求，未完整建模',
                                      '抗震、轴力、扭转、疲劳、预应力、搭接、截断及施工阶段不在本版范围'])
            if s.candidate: s.candidate['status'] = 'checked' if status=='pass' else 'rejected'
        s.revisions.append(dict(revision=s.design_revision, iteration=context['iteration'], candidate=s.candidate.copy(),
                                reason=context['reason'],
                                evaluation=s.evaluation.model_dump(), parameters=context['parameters'].copy(),
                                tools={k:v.model_dump() for k,v in s.tool_results.items()},
                                trace=[t.copy() for t in s.plan_trace if t['revision']==s.design_revision]))
        return {'state':s}

    def next_step(data):
        s = data['state']
        if s.request.task_type != 'new_design' or not s.request.auto_redesign or s.evaluation.status != 'fail': return END
        if context['iteration'] >= s.request.max_iterations:
            s.errors.append('已达到确认的改设轮次上限，未获得通过方案'); return END
        return 'revise'

    def redesign(data):
        s = data['state']; context['minimum_bar_count'] = s.candidate.get('bar_count', context['minimum_bar_count'])+1
        failed=[t for t,ok in s.evaluation.checks.items() if not ok]
        context['reason']='未通过项目：'+','.join(failed)+'；同直径纵筋候选增加至至少'+str(context['minimum_bar_count'])+'根'
        # Fixed supplied dimensions are never changed. Unspecified height can grow within an explicit maximum.
        if not s.candidate and 'beam_depth_mm' not in base and 'max_depth_mm' in base:
            last = s.tool_results.get('design.section_sizing')
            if last and last.status=='success':
                context['parameters']['beam_depth_mm'] = min(base['max_depth_mm'],last.outputs['beam_depth_mm']+50)
                context['reason']+='；在明确上限内调整未固定的梁高'
        s.design_revision += 1
        s.tool_results = {}; s.errors = []; s.evaluation = EvaluationResult()
        return {'state':s}

    graph = StateGraph(dict)
    graph.add_node('design', design); graph.add_node('evaluation', evaluate); graph.add_node('revise', redesign)
    graph.add_conditional_edges(START, lambda d:'design' if d['state'].request.task_type=='new_design' else 'evaluation')
    graph.add_edge('design','evaluation'); graph.add_conditional_edges('evaluation',next_step)
    graph.add_edge('revise','design')
    try:
        return graph.compile().invoke({'state':state}, config={'recursion_limit':3*state.request.max_iterations+5})['state']
    except Exception as exc:
        return error_state(state, f'中国规范工作流异常（{type(exc).__name__}），未形成通过结论')
