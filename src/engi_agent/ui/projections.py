"""Pure projections of actual records. No capacity or compliance recalculation."""
from __future__ import annotations
import json
from engi_agent.engineering.schema import EngineeringState, ToolResult, parameter_python
from engi_agent.engineering.cn_schema import CN_UNITS
from engi_agent.engineering.cn_presentation import CN_FIELDS, LABELS, OUTPUTS
from engi_agent.engineering.presentation import FIELDS, SOURCES, parameter_rows, PARAMETER_HEADERS
from engi_agent.engineering.dependency_graph import SPECS, build_plan, dependencies, TARGET_TOOLS

STAGES={'empty':'未加载','editing':'待校验','validated':'待确认','confirmed':'已确认 · 待运行',
        'parsing':'解析中','running':'执行中','completed':'执行已结束','error':'操作未完成'}
VERDICTS={'pass':'请求项目通过','fail':'请求项目不通过','error':'执行错误','incomplete':'不完整'}
ACTIONS={'execute':'已执行','reuse':'缓存复用','invalidate_execute':'失效重算','blocked':'上游阻断'}
TOOL_STATUS={'success':'执行完成','failed':'执行失败','blocked':'上游阻断'}
GROUPS={
    '几何':['support_type','section_type','load_case','span_mm','beam_width_mm','beam_depth_mm','max_width_mm','max_depth_mm','support_width_mm','cover_mm','shear_position_mm'],
    '材料':['concrete_grade','steel_grade','stirrup_grade','concrete_unit_weight_kn_m3','aggregate_size_mm','importance_factor','design_life_years','safety_class','environment_class'],
    '荷载':['dead_load_kn_m','live_load_kn_m','self_weight_mode','live_combination_factor','live_frequency_factor','live_quasi_factor','design_moment_kn_m','design_shear_kn','crack_limit_mm','deflection_limit_ratio'],
    '配筋':['reinforcement_layers','bar_diameter_mm','bar_count','stirrup_diameter_mm','stirrup_legs','stirrup_spacing_mm'],
    '构造':['end_anchor_length_mm','end_anchor_stirrup_spacing_mm','top_bar_diameter_mm','top_bar_count','side_bar_diameter_mm','side_bar_count_per_face','side_bar_spacing_mm'],
}


def label(key): return FIELDS.get(key,(CN_FIELDS.get(key,key),'其他'))[0]


def editor_rows(state, group):
    rows=[]
    for key in GROUPS[group]:
        item=state.request.parameters.get(key)
        rows.append({'字段':key,'参数':label(key),'输入值':str(item.value) if item else '',
                     '单位':item.unit or '' if item else CN_UNITS[key] or ''})
    return rows


def audit_rows(state):
    return [dict(zip(PARAMETER_HEADERS,row)) for row in parameter_rows(state)]


def result_rows(state):
    rows=[]
    for target in state.request.targets:
        if target not in TARGET_TOOLS: continue
        tool=state.tool_results.get('evaluation.'+TARGET_TOOLS[target])
        value=limit=unit=None
        if tool and tool.status=='success':
            o=tool.outputs
            if target=='flexure':value,limit,unit=o.get('demand_kn_m'),o.get('capacity_kn_m'),'kN·m'
            elif target=='shear':value,limit,unit=o.get('demand_kn'),o.get('capacity_kn'),'kN'
            elif target=='crack':value,limit,unit=o.get('crack_width_mm'),o.get('limit_mm'),'mm'
            elif target=='deflection':value,limit,unit=o.get('deflection_mm'),o.get('limit_mm'),'mm'
        checked=tool.outputs.get('pass') if tool and tool.status=='success' else None
        rows.append({'检查项目':LABELS[target],'实际/作用值':value,'承载力/限值':limit,'单位':unit or '多项条件',
                     '分项结论':'通过' if checked is True else '不通过' if checked is False else '未获得有效结论',
                     '工具执行':TOOL_STATUS.get(tool.status) if tool else '未执行'})
    return rows


def snapshot(state, index=None):
    """Return one recorded round, never merge a historical round with current data."""
    if index is not None and state.revisions:
        return state.revisions[index]
    return {'revision':state.design_revision,'candidate':state.candidate,
            'parameters':{k:parameter_python(k,v) for k,v in state.request.parameters.items()},
            'evaluation':state.evaluation.model_dump(),'tools':{k:v.model_dump() for k,v in state.tool_results.items()},
            'trace':state.plan_trace,'reason':state.revision_reason}


def dag_nodes(state, phase, index=None):
    snap=snapshot(state,index)
    tools={key.split('.',1)[1]:ToolResult.model_validate(value) for key,value in snap['tools'].items()
           if key.startswith(phase+'.')}
    trace={t['tool']:t for t in snap.get('trace',[]) if t['phase']==phase and t['revision']==snap['revision']}
    nodes=[]
    for name,result in tools.items():
        action=trace.get(name,{}).get('action')
        status=('blocked' if result.status=='blocked' else 'error' if result.status=='failed' and not result.outputs.get('engineering_failure')
                else 'failed' if result.status=='failed' else 'reuse' if action=='reuse' else 'executed')
        nodes.append({'name':name,'label':LABELS.get(name,name),'state':status,'action':ACTIONS.get(action,'未记录处理方式'),
                      'reason':trace.get(name,{}).get('reason','历史记录未保存处理原因'),
                      'parents':list(result.inputs.get('upstream',{})), 'result':result})
    if tools: return nodes
    if state.tool_results or state.revisions:
        return []  # This phase was not executed, not an imaginary pending phase.
    params={k:parameter_python(k,v) for k,v in state.request.parameters.items()}
    targets=['flexure','shear'] if phase=='design' else state.request.targets
    if phase=='design' and state.request.task_type!='new_design': return []
    try:
        plan=build_plan(targets,params,design=phase=='design')
        return [dict(name=n,label=LABELS.get(n,n),state='pending',action='待执行计划',reason='尚未运行',
                     parents=list(dependencies(n,params,targets)),result=None) for n in plan]
    except (ValueError,KeyError): return []


def revision_comparison(state, before, after):
    left,right=state.revisions[before],state.revisions[after]
    def actual(r):return {**r.get('parameters',{}),**r.get('candidate',{})}
    a,b=actual(left),actual(right)
    changes=[{'参数':label(k),'修改前':str(a.get(k,'未提供')),'修改后':str(b.get(k,'未提供')),
              '单位':CN_UNITS.get(k) or ''} for k in a.keys()|b.keys()
             if a.get(k)!=b.get(k) and k not in ('status','As_mm2')]
    return sorted(changes,key=lambda r:r['参数'])


def output_rows(result):
    return [{'项目':OUTPUTS.get(k,k),'数值':v if isinstance(v,(int,float)) and not isinstance(v,bool) else None,
             '说明':str(v) if not isinstance(v,(int,float)) else ''} for k,v in result.outputs.items()
            if not isinstance(v,(list,dict)) and k not in ('pass','engineering_failure')]


def input_rows(result):
    rows=[]
    def visit(value,path):
        for key,item in value.items():
            if isinstance(item,dict):visit(item,path+[key])
            elif item is not None and not isinstance(item,list):
                rows.append({'来源':' / '.join(LABELS.get(p,p) for p in path),
                             '输入参数':OUTPUTS.get(key,label(key)),
                             '数值':item if isinstance(item,(float,int)) and not isinstance(item,bool) else None,
                             '说明':str(item) if not isinstance(item,(float,int)) else ''})
    visit(result.inputs.get('parameters',{}),['直接参数'])
    visit(result.inputs.get('upstream',{}),['上游输出'])
    return rows
