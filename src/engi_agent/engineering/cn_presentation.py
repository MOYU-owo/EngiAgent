"""Chinese views of recorded values; no numerical design decisions in this module."""
from .presentation import table, number, parameter_rows, PARAMETER_HEADERS, FIELDS, FIELD_ALIASES, SOURCES

SOURCES['template']='显式案例模板'

LABELS = {
    'materials':'材料参数', 'section_sizing':'截面初选', 'section_geometry':'实际钢筋几何',
    'load_combination':'作用组合', 'beam_analysis':'简支梁内力', 'demand':'设计内力来源',
    'flexural_design':'受弯配筋', 'shear_design':'受剪配箍', 'flexural_check':'独立抗弯验算',
    'shear_check':'独立抗剪验算', 'detailing_check':'适用构造核查', 'crack_check':'裂缝验算',
    'deflection_check':'长期挠度验算', 'flexure':'抗弯', 'shear':'抗剪', 'detailing':'适用构造',
    'crack':'裂缝', 'deflection':'长期挠度',
}
CN_FIELDS = {
    'concrete_grade':'混凝土等级', 'steel_grade':'纵筋牌号', 'stirrup_grade':'箍筋牌号',
    'design_moment_kn_m':'设计弯矩', 'design_shear_kn':'设计剪力',
    'live_quasi_factor':'活载准永久值系数', 'live_combination_factor':'活载组合值系数',
    'live_frequency_factor':'活载频遇值系数', 'importance_factor':'重要性系数',
    'design_life_years':'设计工作年限', 'safety_class':'安全等级', 'environment_class':'环境类别',
    'crack_limit_mm':'裂缝限值', 'end_anchor_length_mm':'端部直锚长度',
    'end_anchor_stirrup_spacing_mm':'锚固区箍筋间距', 'top_bar_diameter_mm':'架立筋直径',
    'top_bar_count':'架立筋根数', 'side_bar_diameter_mm':'腰筋直径',
    'side_bar_count_per_face':'每侧腰筋根数', 'side_bar_spacing_mm':'腰筋间距', 'support_width_mm':'支座宽度',
}
for key,label in CN_FIELDS.items():
    FIELDS.setdefault(key,(label,'中国规范参数'))
    FIELD_ALIASES.setdefault(label,key)

OUTPUTS = {
    'beam_width_mm':'梁宽/mm', 'beam_depth_mm':'梁高/mm', 'effective_depth_mm':'有效高度/mm',
    'gross_inertia_mm4':'毛截面惯性矩/mm⁴', 'bar_area_mm2':'单根纵筋面积/mm²',
    'stirrup_area_mm2':'单肢箍筋面积/mm²', 'fc_mpa':'混凝土抗压设计强度/MPa',
    'ft_mpa':'混凝土抗拉设计强度/MPa', 'ftk_mpa':'混凝土抗拉标准强度/MPa',
    'Ec_mpa':'混凝土弹性模量/MPa', 'Es_mpa':'纵筋弹性模量/MPa', 'fy_mpa':'纵筋抗拉设计强度/MPa',
    'fyv_mpa':'箍筋抗拉设计强度/MPa', 'alpha1':'应力块系数α1', 'beta1':'应力块系数β1',
    'epsilon_cu':'极限压应变', 'xi_b':'界限相对受压区高度', 'sizing_basis':'初选依据',
    'added_self_weight_kn_m':'另计梁自重/(kN/m)', 'total_dead_load_kn_m':'恒载合计/(kN/m)',
    'ultimate_load_kn_m':'承载力设计荷载/(kN/m)', 'standard_load_kn_m':'标准组合荷载/(kN/m)',
    'quasi_load_kn_m':'准永久组合荷载/(kN/m)', 'frequent_load_kn_m':'频遇组合荷载/(kN/m)',
    'combination_load_kn_m':'组合值荷载/(kN/m)', 'governing_combination':'承载力组合',
    'Mu_kn_m':'设计弯矩/(kN·m)', 'Vu_max_kn':'支座中心线剪力/kN', 'Vu_design_kn':'支座边缘设计剪力/kN',
    'critical_shear_position_mm':'受剪检查位置距支座中心/mm', 'reaction_left_kn':'左支座反力/kN',
    'reaction_right_kn':'右支座反力/kN', 'Vu_at_position_kn':'查询剪力/kN',
    'shear_position_mm':'查询位置/mm', 'standard_moment_kn_m':'标准弯矩/(kN·m)',
    'quasi_moment_kn_m':'准永久弯矩/(kN·m)', 'moment_source':'弯矩来源', 'shear_source':'剪力来源',
    'As_mm2':'实配受拉钢筋面积/mm²', 'bar_count':'纵筋根数', 'bar_diameter_mm':'纵筋直径/mm',
    'compression_zone_mm':'受压区高度/mm', 'compression_limit_mm':'受压区高度上限/mm',
    'capacity_kn_m':'抗弯承载力/(kN·m)', 'demand_kn_m':'设计弯矩需求/(kN·m)',
    'minimum_steel_mm2':'最小配筋面积/mm²', 'required_steel_mm2':'需求钢筋面积/mm²', 'utilization':'承载利用率',
    'concrete_capacity_kn':'混凝土抗剪贡献/kN', 'section_limit_kn':'受剪截面上限/kN',
    'demand_kn':'剪力需求/kN', 'capacity_kn':'抗剪承载力/kN', 'Av_mm2':'箍筋总肢面积/mm²',
    'minimum_av_over_s':'最小Asv/s/(mm²/mm)', 'maximum_spacing_mm':'最大箍筋间距/mm',
    'required_av_over_s':'需求Asv/s/(mm²/mm)', 'provided_av_over_s':'实配Asv/s/(mm²/mm)',
    'stirrup_spacing_mm':'箍筋间距/mm', 'stirrup_legs':'箍筋肢数', 'stirrup_diameter_mm':'箍筋直径/mm',
    'arrangement':'布置要求', 'clear_spacing_mm':'下部纵筋净距/mm', 'minimum_clear_spacing_mm':'下部最小净距/mm',
    'top_clear_spacing_mm':'上部纵筋净距/mm', 'required_cover_mm':'保护层下限/mm', 'provided_cover_mm':'实际保护层/mm',
    'required_anchor_mm':'保守直锚长度需求/mm', 'provided_anchor_mm':'直锚长度/mm',
    'side_required_area_per_face_mm2':'每侧腰筋需求/mm²', 'side_area_per_face_mm2':'每侧腰筋实配/mm²',
    'required_top_bar_diameter_mm':'架立筋建议直径/mm', 'rho_te_raw':'有效受拉区原始配筋率',
    'rho_te':'本工具采用有效受拉区配筋率', 'psi':'应变不均匀系数ψ', 'sigma_s_mpa':'准永久钢筋应力/MPa',
    'combination':'正常使用组合', 'cs_mm':'纵筋外缘至底面采用距离/mm', 'deq_mm':'等效钢筋直径/mm',
    'crack_width_mm':'最大裂缝宽度/mm', 'limit_mm':'允许限值/mm', 'rho':'刚度公式受拉配筋率',
    'short_term_stiffness_n_mm2':'短期刚度Bs/(N·mm²)', 'theta':'长期刚度系数θ',
    'long_term_stiffness_n_mm2':'长期刚度B/(N·mm²)', 'deflection_mm':'长期挠度/mm', 'limit_ratio':'挠度限值分母',
}
STATUS = {'pass':'请求项目通过', 'fail':'请求项目不通过', 'error':'执行错误，不能判定通过', 'incomplete':'输入或检查不完整'}


def confirmation_text(state, markdown=False):
    p = state.profile
    lines = ['### 参数确认' if markdown else '\n=== 中国规范 RC 梁参数确认 ===',
             '任务：'+('新设计' if state.request.task_type=='new_design' else '已有梁独立验算'),
             '目标：'+'、'.join(LABELS.get(t,t) for t in state.request.targets),
             table(PARAMETER_HEADERS,parameter_rows(state),markdown=markdown), '依据：'+p.source, p.source_note,
             '组合：1.3Gk+1.5Qk；裂缝与长期挠度：Gk+ψqQk。',
             f'有限改设：{"开启" if state.request.auto_redesign else "关闭"}；最多{state.request.max_iterations}轮。',
             '提供的截面尺寸视为固定；未提供的尺寸按经验初选，增大不得超出明确上限。',
             '理想铰支、无截断搭接；支座采用充分受拉直锚保守方案；施工与节点详图需工程师复核。']
    if state.missing_parameters: lines += ['缺失：'+'、'.join(CN_FIELDS.get(k,FIELDS.get(k,(k,))[0]) for k in state.missing_parameters)]
    return ('\n\n' if markdown else '\n').join(lines)


def overview(state):
    lines = ['计算状态：'+STATUS[state.evaluation.status],
             '范围：本次请求及已实现中国规范项目；工程整体审查仍需节点、施工图与适用边界复核。']
    if state.candidate:
        c=state.candidate
        lines += [f"方案：{number(c['beam_width_mm'])}×{number(c['beam_depth_mm'])} mm；"
                  f"{c['bar_count']}Φ{number(c['bar_diameter_mm'])}；跨内{c['stirrup_legs']}肢Φ{number(c['stirrup_diameter_mm'])}"
                  f"@{number(c['stirrup_spacing_mm'])} mm；锚固区@{number(c['end_anchor_stirrup_spacing_mm'])} mm。"]
    lines += [LABELS.get(k,k)+'：'+('通过' if v else '不通过') for k,v in state.evaluation.checks.items()]
    return '\n'.join(lines)


def markdown_report(state, json_filename=None):
    lines = ['# EngiAgent 中国规范 RC 梁计算报告','', '**计算状态：'+STATUS[state.evaluation.status]+'**','']
    if state.candidate:
        lines += [overview(state).splitlines()[2],'']
    checks=[]
    for target,ok in state.evaluation.checks.items():
        from .dependency_graph import TARGET_TOOLS
        result=state.tool_results.get('evaluation.'+TARGET_TOOLS[target])
        key={'flexure':'capacity_kn_m','shear':'capacity_kn','detailing':'clear_spacing_mm',
             'crack':'crack_width_mm','deflection':'deflection_mm'}[target]
        value=result.outputs.get(key) if result else None
        checks.append([LABELS[target],'通过' if ok else '不通过',OUTPUTS[key]+'：'+number(value,3) if value is not None else '未获得有效计算值'])
    if checks:lines += [table(['检查项目','结果','关键数值'],checks,markdown=True),'']
    lines += ['范围：本次请求及已实现中国规范项目；完整工程审查仍需节点、施工图与适用边界复核。','',
             '## 参数与计算边界','',confirmation_text(state,markdown=True),'',
             '实际计算保留完整精度，以下显示值取整。端部及施工构造假定需落实，分项通过不能替代完整工程审查。','']
    if json_filename: lines += [f'[完整JSON轨迹]({json_filename})','']
    if state.request.user_query: lines += ['原始需求：'+state.request.user_query,'']
    lines += ['## 分项计算过程','']
    for key,result in state.tool_results.items():
        phase,name=key.split('.',1)
        check = '通过' if result.outputs.get('pass') is True else '不通过' if result.outputs.get('pass') is False else '计算完成'
        if result.status!='success': check='执行失败' if result.status=='failed' else '上游阻断'
        lines += [f'### {"设计" if phase=="design" else "独立验算"} · {LABELS.get(name,name)} · {check}','']
        rows=[]
        for k,v in result.outputs.items():
            if k in ('pass','reasons','assumptions','engineering_failure'): continue
            rows.append([OUTPUTS.get(k,k),number(v,4) if isinstance(v,(int,float)) else '未提供/不适用' if v is None else str(v)])
        lines += [table(['项目','结果'],rows,markdown=True),'']
        lines += ['依据：'+'；'.join(ref for ref in result.code_refs if not ref.startswith('docs/')),'']
        lines += ['- '+str(x) for x in result.errors+result.outputs.get('reasons',[])+result.outputs.get('assumptions',[])]+['']
    actions={'execute':'执行','reuse':'复用','invalidate_execute':'失效后重算','blocked':'阻断'}
    lines += ['## 规划与复用记录','',table(['修订','阶段','工具','处理','原因'],
        [[str(t['revision']),'设计' if t['phase']=='design' else '独立验算',LABELS.get(t['tool'],t['tool']),actions[t['action']],t['reason']]
         for t in state.plan_trace],markdown=True),'','## 方案修订','']
    revision_rows=[]
    for r in state.revisions:
        candidate=r['candidate']
        scheme=(number(candidate['beam_width_mm'])+'×'+number(candidate['beam_depth_mm'])+' mm；'
                +str(candidate['bar_count'])+'Φ'+number(candidate['bar_diameter_mm'])) if candidate else '已有方案/未形成候选'
        reason=r.get('reason','历史任务')
        for key in ALL_LABELS(): reason=reason.replace(key,ALL_LABELS()[key])
        revision_rows.append([str(r['revision']),str(r['iteration']),reason,scheme,STATUS[r['evaluation']['status']]])
    lines += [table(['修订','本次轮次','修改原因','候选方案','结果'],revision_rows,markdown=True)]
    lines += ['','## 未覆盖项与停止原因','']
    lines += ['- '+LABELS.get(x.split('：')[-1],x) if x.startswith('本次未请求：') else '- '+x for x in state.evaluation.unimplemented]
    lines += ['- '+e for e in state.errors]
    lines += ['','## 公式与输入追溯','',table(['工具','公式版本','输入哈希'],
        [[k,r.formula_version,r.inputs_hash] for k,r in state.tool_results.items()],markdown=True),'',
        '条文、物理页与适用条件见 docs/rc_beam_cn_design_spec.md；完整精度和历史工具记录见JSON。','']
    return '\n'.join(lines)


def ALL_LABELS():
    return {**LABELS,**{k:v[0] for k,v in FIELDS.items()}}
