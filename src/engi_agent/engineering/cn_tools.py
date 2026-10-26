"""Chinese-code beam arithmetic. No LLM values or executable model code enter here.

Formula contract and applicability: docs/rc_beam_cn_design_spec.md.
"""
import math
from .tools import EngineeringFailure

# GB/T50010 tables 4.1.3/4.1.4/4.1.5; unchanged rows C25-C50.
CONCRETE = {
    'C25': (11.9, 1.27, 1.78, 28000), 'C30': (14.3, 1.43, 2.01, 30000),
    'C35': (16.7, 1.57, 2.20, 31500), 'C40': (19.1, 1.71, 2.39, 32500),
    'C45': (21.1, 1.80, 2.51, 33500), 'C50': (23.1, 1.89, 2.64, 34500),
}
STEEL = {'HPB300': (270, 210000), 'HRB400': (360, 200000), 'HRB500': (435, 200000)}


def materials(p, prior):
    fc, ft, ftk, ec = CONCRETE[p['concrete_grade']]
    fy, es = STEEL[p['steel_grade']]
    if p['concrete_grade']=='C25' and (p['steel_grade']=='HRB500' or p.get('stirrup_grade')=='HRB500'):
        raise EngineeringFailure('采用HRB500钢筋时混凝土不得低于C30（GB55008 2.0.2）')
    stirrup = p.get('stirrup_grade')
    fyv = min(360, STEEL[stirrup][0]) if stirrup else None
    return dict(fc_mpa=fc, ft_mpa=ft, ftk_mpa=ftk, Ec_mpa=ec, fy_mpa=fy,
                fyv_mpa=fyv, Es_mpa=es, alpha1=1.0, beta1=0.8, epsilon_cu=0.0033,
                xi_b=0.8/(1+fy/(es*0.0033)))


def section_sizing(p, prior):
    h = p.get('beam_depth_mm') or math.ceil(p['span_mm']/12/25)*25
    b = p.get('beam_width_mm') or math.ceil(0.5*h/25)*25
    if h > p.get('max_depth_mm', h) or b > p.get('max_width_mm', b):
        raise EngineeringFailure('初选截面超出已确认的尺寸上限')
    return dict(beam_width_mm=b, beam_depth_mm=h,
                sizing_basis='已有尺寸保留；缺失h采用L/12、b采用0.5h、25mm取整（经验初选）')


def section_geometry(p, prior):
    s = prior['section_sizing']; b, h = s['beam_width_mm'], s['beam_depth_mm']
    d = h-p['cover_mm']-p['stirrup_diameter_mm']-p['bar_diameter_mm']/2
    if d <= 0 or b <= 2*(p['cover_mm']+p['stirrup_diameter_mm'])+p['bar_diameter_mm']:
        raise EngineeringFailure('截面净宽或有效高度不足')
    if p.get('span_mm', 1e9)/h < 5:
        raise EngineeringFailure('跨高比小于5，超出普通梁计算边界')
    return {**s, 'effective_depth_mm': d, 'gross_inertia_mm4': b*h**3/12,
            'bar_area_mm2': math.pi*p['bar_diameter_mm']**2/4,
            'stirrup_area_mm2': math.pi*p['stirrup_diameter_mm']**2/4}


def load_combination(p, prior):
    sw = 0.0
    if p['self_weight_mode'] == 'excluded':
        s = prior['section_sizing']
        sw = p['concrete_unit_weight_kn_m3']*s['beam_width_mm']*s['beam_depth_mm']/1e6
    g, q = p['dead_load_kn_m']+sw, p['live_load_kn_m']
    return dict(added_self_weight_kn_m=sw, total_dead_load_kn_m=g,
                ultimate_load_kn_m=1.3*g+1.5*q, standard_load_kn_m=g+q,
                quasi_load_kn_m=g+p['live_quasi_factor']*q,
                frequent_load_kn_m=g+p['live_frequency_factor']*q,
                combination_load_kn_m=g+p['live_combination_factor']*q,
                governing_combination='1.3Gk+1.5Qk（单一不利重力活载）')


def beam_analysis(p, prior):
    loads = prior['load_combination']; span = p['span_mm']/1000
    support = p.get('support_width_mm', 0)/1000
    x = p.get('shear_position_mm', p.get('support_width_mm', 0)/2)/1000
    if not 0 <= x <= span or not 0 <= support < span:
        raise EngineeringFailure('支座宽度或剪力查询位置不在模型范围')
    w = loads['ultimate_load_kn_m']
    return dict(Mu_kn_m=w*span**2/8, Vu_max_kn=w*span/2,
                Vu_design_kn=w*(span-support)/2 if 'support_width_mm' in p else None,
                critical_shear_position_mm=support*500 if 'support_width_mm' in p else None,
                reaction_left_kn=w*span/2, reaction_right_kn=w*span/2,
                Vu_at_position_kn=w*(span/2-x), shear_position_mm=x*1000,
                standard_moment_kn_m=loads['standard_load_kn_m']*span**2/8,
                quasi_moment_kn_m=loads['quasi_load_kn_m']*span**2/8,
                standard_load_kn_m=loads['standard_load_kn_m'], quasi_load_kn_m=loads['quasi_load_kn_m'])


def demand(p, prior):
    a = prior.get('beam_analysis', {})
    return dict(Mu_kn_m=p.get('design_moment_kn_m', a.get('Mu_kn_m')),
                Vu_design_kn=p.get('design_shear_kn', a.get('Vu_design_kn')),
                moment_source='用户确认设计值' if 'design_moment_kn_m' in p else '1.3Gk+1.5Qk内力',
                shear_source='用户确认设计值' if 'design_shear_kn' in p else '支座边缘组合剪力' if a.get('Vu_design_kn') is not None else '未请求/缺少支座数据')


def flexural_values(p, prior, count):
    g, m = prior['section_geometry'], prior['materials']
    b, h, d = g['beam_width_mm'], g['beam_depth_mm'], g['effective_depth_mm']
    area = count*g['bar_area_mm2']; x = m['fy_mpa']*area/(m['alpha1']*m['fc_mpa']*b)
    minimum = max(0.002, 0.45*m['ft_mpa']/m['fy_mpa'])*b*h
    capacity = m['alpha1']*m['fc_mpa']*b*x*(d-x/2)/1e6
    mu = prior['demand']['Mu_kn_m']
    reasons = []
    if x > m['xi_b']*d: reasons.append('超过界限受压区高度，不适用单筋受弯模型')
    if area+1e-8 < minimum: reasons.append('受拉配筋低于最小配筋量')
    if capacity+1e-8 < mu: reasons.append('抗弯承载力不足')
    return dict(As_mm2=area, bar_count=count, compression_zone_mm=x, xi_b=m['xi_b'],
                compression_limit_mm=m['xi_b']*d, capacity_kn_m=capacity, demand_kn_m=mu,
                minimum_steel_mm2=minimum, utilization=mu/capacity if capacity > 0 else None,
                **{'pass': not reasons, 'reasons': reasons})


def flexural_design(p, prior):
    g, m = prior['section_geometry'], prior['materials']
    b, h, d = g['beam_width_mm'], g['beam_depth_mm'], g['effective_depth_mm']
    mu = prior['demand']['Mu_kn_m']*1e6
    disc = d*d-2*mu/(m['alpha1']*m['fc_mpa']*b)
    if disc < 0: raise EngineeringFailure('截面抗弯不足，无法求得单筋解')
    x = 2*mu/(m['alpha1']*m['fc_mpa']*b*(d+math.sqrt(disc))) if mu else 0
    if x > m['xi_b']*d: raise EngineeringFailure('需求超过单筋适筋截面上限')
    required = max(m['alpha1']*m['fc_mpa']*b*x/m['fy_mpa'],
                   max(.002, .45*m['ft_mpa']/m['fy_mpa'])*b*h)
    count = max(2, p.get('minimum_bar_count', 2), math.ceil(required/g['bar_area_mm2']))
    values = flexural_values(p, prior, count)
    if not values['pass']: raise EngineeringFailure('整数根数选择后不满足单筋截面条件')
    return {**values, 'required_steel_mm2': required, 'bar_diameter_mm': p['bar_diameter_mm']}


def flexural_check(p, prior):
    return flexural_values(p, prior, p['bar_count'])


def shear_values(p, prior):
    g, m = prior['section_geometry'], prior['materials']
    b, d, h = g['beam_width_mm'], g['effective_depth_mm'], g['beam_depth_mm']
    hw = d  # rectangle: hw=h0, GB50010 6.3.1
    ratio = hw/b
    if ratio > 6: raise EngineeringFailure('腹板高宽比大于6，超出当前受剪工具范围')
    coefficient = .25 if ratio <= 4 else .25-(ratio-4)*.025
    vmax = coefficient*m['fc_mpa']*b*d/1000  # beta_c=1 for C<=50
    vc = .7*m['ft_mpa']*b*d/1000
    demand_v = prior['demand']['Vu_design_kn']
    av = p['stirrup_legs']*g['stirrup_area_mm2']
    minratio = .24*m['ft_mpa']/m['fyv_mpa']*b if demand_v > vc else 0.0
    # 9.2.9 table: h<=150, 150<h<=300, 300<h<=500, 500<h<=800, h>800.
    high = demand_v > vc
    maxs = (150 if high else 200) if h <= 300 else (200 if high else 300) if h <= 500 else (250 if high else 350) if h <= 800 else (300 if high else 400)
    return dict(concrete_capacity_kn=vc, section_limit_kn=vmax, demand_kn=demand_v,
                Av_mm2=av, minimum_av_over_s=minratio, maximum_spacing_mm=maxs,
                required_av_over_s=max(minratio, max(0, demand_v-vc)*1000/(m['fyv_mpa']*d)))


def shear_design(p, prior):
    t = shear_values(p, prior)
    if t['demand_kn'] > t['section_limit_kn']: raise EngineeringFailure('剪力超过受剪截面上限')
    required = t['required_av_over_s']
    s = math.floor(min(t['maximum_spacing_mm'], t['Av_mm2']/required if required else t['maximum_spacing_mm'])/10)*10
    if s < 50: raise EngineeringFailure('需求箍筋间距小于本程序候选下限50mm')
    return {**t, 'stirrup_spacing_mm': s, 'stirrup_legs': p['stirrup_legs'],
            'stirrup_diameter_mm': p['stirrup_diameter_mm'], 'arrangement': '跨内采用同一间距；支座内锚固区另按确认间距；首箍距支座边缘不大于50mm'}


def shear_check(p, prior):
    t = shear_values(p, prior); m, g = prior['materials'], prior['section_geometry']
    avs = t['Av_mm2']/p['stirrup_spacing_mm']
    cap = t['concrete_capacity_kn']+m['fyv_mpa']*avs*g['effective_depth_mm']/1000
    reasons = []
    if t['demand_kn'] > t['section_limit_kn']: reasons.append('超过受剪截面上限')
    if cap+1e-8 < t['demand_kn']: reasons.append('斜截面抗剪承载力不足')
    if avs+1e-8 < t['minimum_av_over_s']: reasons.append('低于最小配箍率')
    if p['stirrup_spacing_mm'] > t['maximum_spacing_mm']: reasons.append('箍筋间距超限')
    return {**t, 'capacity_kn': cap, 'provided_av_over_s': avs, 'pass': not reasons, 'reasons': reasons}


def detailing_check(p, prior):
    g, m = prior['section_geometry'], prior['materials']; b, h = g['beam_width_mm'], g['beam_depth_mm']
    count, diameter = p['bar_count'], p['bar_diameter_mm']
    clear = (b-2*(p['cover_mm']+p['stirrup_diameter_mm'])-count*diameter)/(count-1)
    minclear = max(25, diameter, 4*p['aggregate_size_mm']/3)
    required_cover = max(20, 25 if p['concrete_grade']=='C25' else 20)
    # Straight tension anchorage, ribbed rebar, no beneficial reduction factors.
    lab = .14*m['fy_mpa']/m['ft_mpa']*diameter
    la = max(200, lab*(1.1 if diameter > 25 else 1))
    top_min = 8 if p['span_mm'] < 4000 else 10 if p['span_mm'] <= 6000 else 12
    hw = g['effective_depth_mm']
    side_required = .001*b*hw if hw >= 450 else 0
    side_area = p['side_bar_count_per_face']*math.pi*p['side_bar_diameter_mm']**2/4
    reasons = []
    if clear < minclear: reasons.append('下部纵筋净距不足，单层布置不可行')
    if p['cover_mm'] < required_cover: reasons.append('一类环境保护层不足')
    if p['cover_mm'] < p['stirrup_diameter_mm'] or p['cover_mm']+p['stirrup_diameter_mm'] < max(diameter,p['top_bar_diameter_mm']):
        reasons.append('钢筋保护层小于相应钢筋公称直径')
    if diameter < (10 if h>=300 else 8): reasons.append('下部纵筋直径低于梁高对应下限')
    if p['stirrup_diameter_mm'] < max(6, diameter/4): reasons.append('箍筋直径不足')
    if h>800 and p['stirrup_diameter_mm']<8: reasons.append('梁高大于800mm，箍筋直径低于建议值8mm')
    top_clear = (b-2*(p['cover_mm']+p['stirrup_diameter_mm'])-p['top_bar_count']*p['top_bar_diameter_mm'])/(p['top_bar_count']-1)
    if top_clear < max(30,1.5*p['top_bar_diameter_mm']): reasons.append('上部钢筋净距不足')
    if p['top_bar_diameter_mm'] < top_min: reasons.append('架立筋直径不足')
    if p['end_anchor_length_mm'] < la: reasons.append('不满足本方案采用的保守全长直锚要求')
    if p['cover_mm']+p['stirrup_diameter_mm'] <= 5*diameter and p['end_anchor_stirrup_spacing_mm'] > min(5*diameter,100):
        reasons.append('锚固范围横向钢筋间距不足以满足一般受拉直锚构造')
    if p['end_anchor_length_mm'] > p['support_width_mm']-p['cover_mm']:
        reasons.append('声明的直锚长度不能容纳于支座，需补充节点/弯锚设计（当前不支持）')
    if side_area+1e-8 < side_required: reasons.append('每侧腰筋面积不足')
    if side_required and (not p.get('side_bar_spacing_mm') or p['side_bar_spacing_mm'] > 200):
        reasons.append('腰筋间距缺失或大于200mm')
    vertical_clear_centers = h-2*(p['cover_mm']+p['stirrup_diameter_mm'])-(diameter+p['top_bar_diameter_mm'])/2
    if side_required and p.get('side_bar_spacing_mm') and vertical_clear_centers > (p['side_bar_count_per_face']+1)*p['side_bar_spacing_mm']+1e-8:
        reasons.append('腰筋根数与声明的最大竖向间距不相容')
    return dict(clear_spacing_mm=clear, top_clear_spacing_mm=top_clear, minimum_clear_spacing_mm=minclear, required_cover_mm=required_cover,
                provided_cover_mm=p['cover_mm'], required_anchor_mm=la, provided_anchor_mm=p['end_anchor_length_mm'],
                side_required_area_per_face_mm2=side_required, side_area_per_face_mm2=side_area,
                required_top_bar_diameter_mm=top_min, **{'pass': not reasons, 'reasons': reasons},
                assumptions=['理想铰支、无部分转动约束；全跨等截面等配筋，无截断或搭接',
                             '端部采用一般充分受拉直锚保守方案，并非9.2.2简支端部伸入长度的唯一要求',
                             '不宜类构造推荐值按本项目接受标准检查，不改写其规范效力',
                             '不计上部架立筋对受弯承载力和长期刚度的有利作用',
                             '第一道箍筋距支座边缘≤50mm、封闭箍及拉结要求应在施工图落实'])


def service_values(p, prior, *, crack):
    g, m, a = prior['section_geometry'], prior['materials'], prior['beam_analysis']
    area = p['bar_count']*g['bar_area_mm2']; d = g['effective_depth_mm']
    rho_raw = area/(.5*g['beam_width_mm']*g['beam_depth_mm'])
    rho_te = max(.01, rho_raw) if crack else rho_raw
    sigma = a['quasi_moment_kn_m']*1e6/(.87*d*area)
    if sigma > m['fy_mpa']:
        raise EngineeringFailure('正常使用钢筋应力已超过设计强度，超出当前裂缝/刚度模型范围')
    psi = min(1, max(.2, 1.1-.65*m['ftk_mpa']/(rho_te*sigma))) if sigma else .2
    return dict(As_mm2=area, rho_te_raw=rho_raw, rho_te=rho_te, psi=psi, sigma_s_mpa=sigma,
                quasi_moment_kn_m=a['quasi_moment_kn_m'], combination='准永久组合Gk+ψqQk')


def crack_check(p, prior):
    v = service_values(p, prior, crack=True); m = prior['materials']
    cs = min(65, max(20, p['cover_mm']+p['stirrup_diameter_mm']))
    w = 1.9*v['psi']*v['sigma_s_mpa']/m['Es_mpa']*(1.9*cs+.08*p['bar_diameter_mm']/v['rho_te'])
    ok = w <= p['crack_limit_mm']
    return {**v, 'cs_mm': cs, 'deq_mm': p['bar_diameter_mm'], 'crack_width_mm': w,
            'limit_mm': p['crack_limit_mm'], 'pass': ok, 'reasons': [] if ok else ['最大裂缝宽度超限']}


def deflection_check(p, prior):
    v = service_values(p, prior, crack=False); m, g = prior['materials'], prior['section_geometry']
    rho = v['As_mm2']/(g['beam_width_mm']*g['effective_depth_mm'])
    bs = m['Es_mpa']*v['As_mm2']*g['effective_depth_mm']**2/(1.15*v['psi']+.2+6*m['Es_mpa']/m['Ec_mpa']*rho)
    stiffness = bs/2  # no beneficial compression reinforcement included
    f = 5*prior['beam_analysis']['quasi_load_kn_m']*p['span_mm']**4/(384*stiffness)
    # Table 3.4.3: ordinary roof/floor, no special deflection requirement.
    code_ratio = 200 if p['span_mm'] < 7000 else 250 if p['span_mm'] <= 9000 else 300
    ratio = max(code_ratio, p['deflection_limit_ratio'])
    limit = p['span_mm']/ratio; ok = f <= limit
    return {**v, 'rho': rho, 'short_term_stiffness_n_mm2': bs, 'theta': 2,
            'long_term_stiffness_n_mm2': stiffness, 'deflection_mm': f,
            'limit_mm': limit, 'limit_ratio': ratio, 'pass': ok,
            'reasons': [] if ok else ['考虑长期作用的挠度超限']}


REGISTRY = {fn.__name__: fn for fn in (materials, section_sizing, section_geometry, load_combination,
            beam_analysis, demand, flexural_design, shear_design, flexural_check, shear_check, detailing_check,
            crack_check, deflection_check)}
