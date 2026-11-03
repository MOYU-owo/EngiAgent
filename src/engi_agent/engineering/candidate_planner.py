"""LLM chooses design variables; deterministic boundaries and checks remain binding."""
import math
from .roles import CandidateDecision


def propose(search, state, parameters, minimum_count, roles, attempts, remaining):
    tried=[dict(beam_width_mm=k[0],beam_depth_mm=k[1],bar_diameter_mm=k[2],minimum_bar_count=k[3])
           for k in sorted(search.seen)]
    history=[]
    for revision in attempts:
        history.append(dict(revision=revision['revision'],candidate=revision['candidate'],
            checks=revision['evaluation']['checks'],status=revision['evaluation']['status'],
            reasons={k:v['outputs'].get('reasons',v.get('errors',[])) for k,v in revision['tools'].items()
                     if k.startswith('evaluation.') and (v['outputs'].get('reasons') or v.get('errors'))}))
    payload=dict(parameters=parameters,minimum_bar_count=minimum_count,domain=search.domain,
        allowed_diameters=search.diameters,tried=tried,history=history,remaining_attempts=remaining,
        solution_count=state.request.solution_count,
        verified_results={k:v.outputs for k,v in state.tool_results.items() if k.startswith('evaluation.')},
        preference=search.preference.model_dump() if search.preference else None)
    event=dict(mode='llm',source='DeepSeek',after_revision=state.design_revision,status='requested')
    search.selection_trace.append(event)
    try:
        decision=CandidateDecision.model_validate(roles.choose_candidate(payload))
        event['decision']=decision.model_dump()
        if decision.stop:
            event['status']='stopped'
            return None
        p=parameters.copy()
        for key,domain in search.domain.items():
            value=getattr(decision,key)
            if value is None:value=p[key]
            if not math.isfinite(value) or not domain['initial_mm']<=value<=domain['maximum_mm']:
                raise ValueError('截面超出已确认范围')
            if domain['fixed'] and value!=domain['initial_mm']:
                raise ValueError('不能修改固定截面')
            if not domain['fixed'] and not math.isclose((value-domain['initial_mm'])/domain['step_mm'],
                    round((value-domain['initial_mm'])/domain['step_mm']),abs_tol=1e-8):
                raise ValueError('截面不符合搜索步长')
            p[key]=value
        if decision.bar_diameter_mm is not None:p['bar_diameter_mm']=decision.bar_diameter_mm
        if p['bar_diameter_mm'] not in search.diameters:raise ValueError('直径未获允许')
        key=search.key(p,decision.minimum_bar_count)
        if key in search.seen:raise ValueError('候选重复')
        search.seen.add(key)
        event.update(status='accepted',parameters=p.copy(),minimum_bar_count=decision.minimum_bar_count,
                     reason=decision.reason)
        return p,decision.minimum_bar_count,'Design Agent：'+decision.reason
    except Exception as exc:
        # Preserve the rejection for audit; never silently pretend a rule is an LLM decision.
        event.update(status='rejected',error_type=type(exc).__name__)
        if isinstance(exc,ValueError):event['rejection_reason']=str(exc) if type(exc) is ValueError else '结构化决策无效'
        raise
