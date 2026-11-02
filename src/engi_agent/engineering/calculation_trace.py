"""Display derivations from recorded inputs/outputs; never evaluates generated code.

Numeric results and final verdicts come from the engineering tool record. Formatting
uses six significant digits; full precision remains in the structured tool record.
"""
from __future__ import annotations


def calculation_steps(record):
    if record.status != 'success':
        return [dict(step=1, title='未完成计算', formula='上游/工具异常', substitution='；'.join(record.errors), result='未形成有效数值或通过结论', unit='', passed=None)]
    p=record.inputs.get('parameters',{}); u=record.inputs.get('upstream',{}); o=record.outputs
    g=u.get('section_geometry',{}); m=u.get('materials',{}); a=u.get('beam_analysis',{}); d=u.get('demand',{})
    rows=[]
    def n(value):
        return f'{value:.8g}' if isinstance(value,(float,int)) and not isinstance(value,bool) else str(value)
    def add(title, formula, substitution, result, unit=''):
        rows.append(dict(step=len(rows)+1,title=title,formula=formula,substitution=substitution,result=result,unit=unit,passed=None))
    name=record.tool
    if name=='section_sizing':
        add('截面采用', '固定值保留；缺失h按ceil(L/12/25)×25；缺失b按ceil(0.5h/25)×25',
            str(p), f"{o['beam_width_mm']}×{o['beam_depth_mm']}", 'mm')
    elif name=='materials':
        for key in ('fc_mpa','ft_mpa','ftk_mpa','fy_mpa','fyv_mpa','Ec_mpa','Es_mpa'):
            add('材料表取值 '+key, '按已确认材料牌号查程序材料表', str(p), o.get(key), 'MPa')
        add('界限相对受压区高度', 'ξb=β1/[1+fy/(Es×εcu)]', f"{m.get('beta1',o['beta1'])}/[1+{o['fy_mpa']}/({o['Es_mpa']}×{o['epsilon_cu']})]", o['xi_b'])
    elif name=='section_geometry':
        s=u['section_sizing']
        add('有效高度', 'h0=h-c-dsv-d/2', f"{s['beam_depth_mm']}-{p['cover_mm']}-{p['stirrup_diameter_mm']}-{p['bar_diameter_mm']}/2",o['effective_depth_mm'],'mm')
        add('单根纵筋面积','A1=πd²/4',f"π×{p['bar_diameter_mm']}²/4",o['bar_area_mm2'],'mm²')
        add('单肢箍筋面积','Asv,1=πdsv²/4',f"π×{p['stirrup_diameter_mm']}²/4",o['stirrup_area_mm2'],'mm²')
        add('毛截面惯性矩','I=bh³/12',f"{s['beam_width_mm']}×{s['beam_depth_mm']}³/12",o['gross_inertia_mm4'],'mm⁴')
    elif name=='load_combination':
        s=u.get('section_sizing',{})
        add('另计自重','gself=γc×b×h/10⁶（输入已含自重时为0）',
            f"{p.get('concrete_unit_weight_kn_m3')}×{s.get('beam_width_mm')}×{s.get('beam_depth_mm')}/10⁶" if p['self_weight_mode']=='excluded' else '已含自重，不重复计入',o['added_self_weight_kn_m'],'kN/m')
        add('恒载合计','Gk=输入恒载+另计自重',f"{p['dead_load_kn_m']}+{n(o['added_self_weight_kn_m'])}",o['total_dead_load_kn_m'],'kN/m')
        for title,key,coef in [('承载力组合','ultimate_load_kn_m',1.5),('准永久组合','quasi_load_kn_m',p['live_quasi_factor']),('标准组合','standard_load_kn_m',1),('频遇组合','frequent_load_kn_m',p['live_frequency_factor']),('组合值','combination_load_kn_m',p['live_combination_factor'])]:
            factor=1.3 if key=='ultimate_load_kn_m' else 1
            add(title,'q=αGk+βQk',f"{factor}×{n(o['total_dead_load_kn_m'])}+{coef}×{p['live_load_kn_m']}",o[key],'kN/m')
    elif name=='beam_analysis':
        loads=u['load_combination'];L=p['span_mm']/1000
        for title,key,qkey in [('设计弯矩','Mu_kn_m','ultimate_load_kn_m'),('标准弯矩','standard_moment_kn_m','standard_load_kn_m'),('准永久弯矩','quasi_moment_kn_m','quasi_load_kn_m')]:
            add(title,'M=qL²/8',f"{n(loads[qkey])}×{L}²/8",o[key],'kN·m')
        add('支座中心剪力','V=qL/2',f"{n(loads['ultimate_load_kn_m'])}×{L}/2",o['Vu_max_kn'],'kN')
        if o.get('Vu_design_kn') is not None:
            add('支座边缘剪力','V=q(L-bsupport)/2',f"{n(loads['ultimate_load_kn_m'])}×({L}-{p['support_width_mm']/1000})/2",o['Vu_design_kn'],'kN')
    elif name=='demand':
        add('弯矩来源','确认设计内力或荷载分析值',o['moment_source'],o['Mu_kn_m'],'kN·m')
        add('剪力来源','确认设计内力或支座边缘剪力',o['shear_source'],o['Vu_design_kn'],'kN')
    elif name in ('flexural_design','flexural_check'):
        count=o['bar_count'];area=o['As_mm2']
        add('实配钢筋面积','As=nA1',f"{count}×{n(g['bar_area_mm2'])}",area,'mm²')
        add('受压区高度','x=fyAs/(α1fcb)',f"{m['fy_mpa']}×{n(area)}/({m['alpha1']}×{m['fc_mpa']}×{g['beam_width_mm']})",o['compression_zone_mm'],'mm')
        add('受压区上限','xb=ξb×h0',f"{n(m['xi_b'])}×{g['effective_depth_mm']}",o['compression_limit_mm'],'mm')
        add('最小配筋面积','As,min=max(0.002,0.45ft/fy)bh',f"max(0.002,0.45×{m['ft_mpa']}/{m['fy_mpa']})×{g['beam_width_mm']}×{g['beam_depth_mm']}",o['minimum_steel_mm2'],'mm²')
        add('抗弯承载力','Mu=fyAs(h0-x/2)/10⁶',f"{m['fy_mpa']}×{n(area)}×({g['effective_depth_mm']}-{n(o['compression_zone_mm'])}/2)/10⁶",o['capacity_kn_m'],'kN·m')
        add('受弯比较','M需求≤Mu，且As≥As,min、x≤xb',f"{n(o['demand_kn_m'])}≤{n(o['capacity_kn_m'])}；{n(area)}≥{n(o['minimum_steel_mm2'])}；{n(o['compression_zone_mm'])}≤{n(o['compression_limit_mm'])}",'见工具总判定')
    elif name in ('shear_design','shear_check'):
        add('混凝土抗剪贡献','Vc=0.7ftbh0/1000',f"0.7×{m['ft_mpa']}×{g['beam_width_mm']}×{g['effective_depth_mm']}/1000",o['concrete_capacity_kn'],'kN')
        ratio=g['effective_depth_mm']/g['beam_width_mm']
        coefficient=.25 if ratio<=4 else .25-(ratio-4)*.025
        add('受剪截面上限','Vmax=β×fc×b×h0/1000；h0/b≤4时β=0.25，4至6间线性取值',
            f"{coefficient}×{m['fc_mpa']}×{g['beam_width_mm']}×{g['effective_depth_mm']}/1000",o['section_limit_kn'],'kN')
        add('箍筋肢面积合计' ,'Asv=nlegs×Asv,1',f"{p['stirrup_legs']}×{n(g['stirrup_area_mm2'])}",o['Av_mm2'],'mm²')
        add('需求配箍','Asv/s≥max(最小配箍, (V-Vc)×1000/(fyvh0))',f"max({n(o['minimum_av_over_s'])},max(0,{n(o['demand_kn'])}-{n(o['concrete_capacity_kn'])})×1000/({m['fyv_mpa']}×{g['effective_depth_mm']}))",o['required_av_over_s'],'mm²/mm')
        if name=='shear_check':
            add('受剪承载力','Vu=Vc+fyv(Asv/s)h0/1000',f"{n(o['concrete_capacity_kn'])}+{m['fyv_mpa']}×({n(o['Av_mm2'])}/{p['stirrup_spacing_mm']})×{g['effective_depth_mm']}/1000",o['capacity_kn'],'kN')
        else:
            add('选用箍筋间距','s=10×floor(min(smax,Asv/需求)/10)；需求为0时取smax',f"Asv={n(o['Av_mm2'])}；需求={n(o['required_av_over_s'])}；smax={o['maximum_spacing_mm']}",o['stirrup_spacing_mm'],'mm')
        add('受剪截面及间距限制','V≤V截面上限；s≤smax',f"V={n(o['demand_kn'])}；V上限={n(o['section_limit_kn'])}；smax={o['maximum_spacing_mm']}",'并计入工具总判定')
    elif name=='detailing_check':
        add('下部净距','snet=[b-2(c+dsv)-nd]/(n-1)',f"[{g['beam_width_mm']}-2×({p['cover_mm']}+{p['stirrup_diameter_mm']})-{p['bar_count']}×{p['bar_diameter_mm']}]/({p['bar_count']}-1)",o['clear_spacing_mm'],'mm')
        add('最小净距','smin=max(25,d,4Dagg/3)',f"max(25,{p['bar_diameter_mm']},4×{p['aggregate_size_mm']}/3)",o['minimum_clear_spacing_mm'],'mm')
        add('直锚需求','la=max(200,0.14fy/ft×d×ζa)，d>25时ζa=1.1',f"max(200,0.14×{m['fy_mpa']}/{m['ft_mpa']}×{p['bar_diameter_mm']}×{1.1 if p['bar_diameter_mm']>25 else 1})",o['required_anchor_mm'],'mm')
        add('上部纵筋净距','snet,top=[b-2(c+dsv)-ntop dtop]/(ntop-1)',
            f"[{g['beam_width_mm']}-2×({p['cover_mm']}+{p['stirrup_diameter_mm']})-{p['top_bar_count']}×{p['top_bar_diameter_mm']}]/({p['top_bar_count']}-1)",o['top_clear_spacing_mm'],'mm')
        add('每侧腰筋面积','As,side=nside×πdside²/4',f"{p['side_bar_count_per_face']}×π×{p['side_bar_diameter_mm']}²/4",o['side_area_per_face_mm2'],'mm²')
        add('每侧腰筋需求','h0≥450时As,side≥0.001bh0',f"h0={g['effective_depth_mm']}；0.001×{g['beam_width_mm']}×{g['effective_depth_mm']}",o['side_required_area_per_face_mm2'],'mm²')
        for title,key,actual in [('保护层' ,'required_cover_mm',o['provided_cover_mm']),('直锚','required_anchor_mm',o['provided_anchor_mm']),('每侧腰筋','side_required_area_per_face_mm2',o['side_area_per_face_mm2'])]:
            add(title+'比较','实配值≥需求值',f"{n(actual)}≥{n(o[key])}",'见构造总判定')
    elif name in ('crack_check','deflection_check'):
        add('实配钢筋面积','As=n×A1',f"{p['bar_count']}×{n(g['bar_area_mm2'])}",o['As_mm2'],'mm²')
        add('钢筋应力','σs=Mq×10⁶/(0.87h0As)',f"{n(o['quasi_moment_kn_m'])}×10⁶/(0.87×{g['effective_depth_mm']}×{n(o['As_mm2'])})",o['sigma_s_mpa'],'MPa')
        add('有效受拉区配筋率','ρte=As/(0.5bh)；裂缝采用max(ρte,0.01)，刚度用原值',f"{n(o['As_mm2'])}/(0.5×{g['beam_width_mm']}×{g['beam_depth_mm']})",o['rho_te'])
        add('应变不均匀系数','ψ=clamp(1.1-0.65ftk/(ρteσs),0.2,1)；σs=0时取0.2',f"clamp(1.1-0.65×{m['ftk_mpa']}/({n(o['rho_te'])}×{n(o['sigma_s_mpa'])}),0.2,1)" if o['sigma_s_mpa'] else 'σs=0，使用显式零荷载分支',o['psi'])
        if name=='crack_check':
            add('保护层距离','cs=clamp(c+dsv,20,65)',f"clamp({p['cover_mm']}+{p['stirrup_diameter_mm']},20,65)",o['cs_mm'],'mm')
            add('裂缝宽度','w=1.9ψσs/Es×(1.9cs+0.08deq/ρte)',f"1.9×{n(o['psi'])}×{n(o['sigma_s_mpa'])}/{m['Es_mpa']}×(1.9×{o['cs_mm']}+0.08×{o['deq_mm']}/{n(o['rho_te'])})",o['crack_width_mm'],'mm')
            add('裂缝比较','w≤wlim',f"{n(o['crack_width_mm'])}≤{o['limit_mm']}",'通过' if o['pass'] else '不通过')
        else:
            add('截面配筋率','ρ=As/(bh0)',f"{n(o['As_mm2'])}/({g['beam_width_mm']}×{g['effective_depth_mm']})",o['rho'])
            add('短期刚度','Bs=EsAsh0²/(1.15ψ+0.2+6Es/Ec×ρ)',f"{m['Es_mpa']}×{n(o['As_mm2'])}×{g['effective_depth_mm']}²/(1.15×{n(o['psi'])}+0.2+6×{m['Es_mpa']}/{m['Ec_mpa']}×{n(o['rho'])})",o['short_term_stiffness_n_mm2'],'N·mm²')
            add('长期刚度','B=Bs/θ',f"{n(o['short_term_stiffness_n_mm2'])}/{o['theta']}",o['long_term_stiffness_n_mm2'],'N·mm²')
            add('长期挠度','f=5qqL⁴/(384B)',f"5×{n(a['quasi_load_kn_m'])}×{p['span_mm']}⁴/(384×{n(o['long_term_stiffness_n_mm2'])})",o['deflection_mm'],'mm')
            add('挠度限值','flim=L/r，r取规范和用户要求中的较严者',f"{p['span_mm']}/{o['limit_ratio']}",o['limit_mm'],'mm')
            add('挠度比较','f≤flim',f"{n(o['deflection_mm'])}≤{n(o['limit_mm'])}",'通过' if o['pass'] else '不通过')
    if 'pass' in o:
        add('工具总判定','所有适用判据同时满足', '；'.join(o.get('reasons',[])) or '已记录检查无不满足项','通过' if o['pass'] else '不通过')
        rows[-1]['passed']=o['pass']
    return rows
