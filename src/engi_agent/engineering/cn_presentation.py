"""Deterministic Chinese engineering views shared by terminal and Markdown.

Formatting is display-only: full precision remains in state/JSON and checks are
never recomputed from rounded display values.
"""
from __future__ import annotations
from .references import professional_references

from pathlib import Path
from uuid import uuid4
from .cn_schema import EngineeringState
from decimal import Decimal, ROUND_HALF_UP
import re
import unicodedata
from .cn_schema import ProgressEvent


# Insertion order is the stable row order used for numbered CLI edits.
FIELDS = {
    "support_type": ("支承形式", "基本条件"),
    "section_type": ("截面形式", "基本条件"),
    "load_case": ("荷载形式", "基本条件"),
    "span_mm": ("跨度", "几何"),
    "beam_width_mm": ("梁宽", "几何"),
    "beam_depth_mm": ("梁高", "几何"),
    "max_width_mm": ("最大梁宽", "几何约束"),
    "max_depth_mm": ("最大梁高", "几何约束"),
    "cover_mm": ("净保护层", "几何"),
    "concrete_unit_weight_kn_m3": ("混凝土容重", "材料"),
    "bar_diameter_mm": ("纵筋直径", "纵筋"),
    "bar_count": ("纵筋根数", "纵筋"),
    "reinforcement_layers": ("受拉纵筋层数", "纵筋"),
    "stirrup_diameter_mm": ("箍筋直径", "箍筋"),
    "stirrup_legs": ("箍筋肢数", "箍筋"),
    "stirrup_spacing_mm": ("箍筋间距", "箍筋"),
    "aggregate_size_mm": ("最大骨料粒径", "布置"),
    "dead_load_kn_m": ("输入恒载", "荷载"),
    "live_load_kn_m": ("活载", "荷载"),
    "self_weight_mode": ("自重约定", "荷载"),
    "shear_position_mm": ("剪力查询位置", "分析"),
    "deflection_limit_ratio": ("挠度限值分母", "正常使用"),
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
for key, label in CN_FIELDS.items():
    FIELDS[key] = (label, '中国规范参数')

FIELD_ALIASES = {label: key for key, (label, _) in FIELDS.items()}
FIELD_ALIASES.update({"梁跨度": "span_mm", "保护层": "cover_mm", "钢筋根数": "bar_count"})
FIELD_ALIASES.update({"恒载": "dead_load_kn_m", "活荷载": "live_load_kn_m"})
ENUMS = {
    "simply_supported": "简支", "rectangular": "矩形", "full_span_udl": "全跨均布",
    "included": "输入恒载已含自重，不重复计入",
    "excluded": "输入恒载不含自重，程序另行计入",
}
ENUM_INPUTS = {"简支": "simply_supported", "矩形": "rectangular", "全跨均布": "full_span_udl",
               "已含自重": "included", "另计自重": "excluded"}
SOURCES = {"user": "用户/任务文件", "llm_extracted": "模型提取", "tool": "计算工具",
           "derived": "推导", "default_confirmed": "已确认假设", "template": "显式案例模板"}
TARGETS = {"flexure": "抗弯", "shear": "抗剪", "detailing": "适用构造", "crack": "裂缝", "deflection": "长期挠度"}
TOOLS = {"materials": "材料参数", "section_sizing": "截面初选", "section_geometry": "实际钢筋几何",
         "load_combination": "作用组合", "beam_analysis": "简支梁内力", "demand": "设计内力来源",
         "flexural_design": "受弯配筋", "shear_design": "受剪配箍", "flexural_check": "独立抗弯验算",
         "shear_check": "独立抗剪验算", "detailing_check": "适用构造核查", "crack_check": "裂缝验算",
         "deflection_check": "长期挠度验算"}
PHASES = {"design": "设计", "evaluation": "独立验算"}
UNITS = {"mm2": "mm²", "kN/m3": "kN/m³"}


def plain(value) -> str:
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", str(value))
    return "".join(" " if unicodedata.category(c).startswith("C") else c for c in text)


def number(value, decimals=2) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "是" if value else "否"
    if not isinstance(value, (int, float)):
        return plain(value)
    if value == 0:
        return "0"
    if abs(value) < 0.01 or abs(value) >= 1e18:
        return f"{value:.4g}"
    # Remove binary float tails before display rounding (112.27499999999999 ->
    # 112.275 -> 112.28). This never alters stored values or pass decisions.
    rounded = Decimal(format(value, ".15g")).quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    text = f"{rounded:,.{decimals}f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def quantity(value, unit="", decimals=2):
    return number(value, decimals) + (" " + UNITS.get(unit, unit) if unit else "")


def parameter_value(key, value, unit=None, raw=False):
    if isinstance(value, str) and value in ENUMS:
        return ENUMS[value]
    if key in {"bar_count", "stirrup_legs", "reinforcement_layers"}:
        return number(float(value))
    if key == "deflection_limit_ratio":
        if raw and isinstance(value, str) and re.fullmatch(r'[Ll]\s*/\s*\d+(?:\.\d+)?', value.strip()):
            return plain(value)
        return "L/" + number(value)
    if raw and isinstance(value, (int, float)) and not isinstance(value, bool):
        return format(value, ".15g") + (" " + UNITS.get(unit, unit) if unit else "")
    return quantity(value, unit or "")


def field_label(key):
    return FIELDS.get(key, (key, "其他"))[0]


def friendly_message(text):
    text = plain(text)
    for phase, phase_name in PHASES.items():
        for tool, label in TOOLS.items():
            text = text.replace(phase + "." + tool, phase_name + "·" + label)
    for tool, label in TOOLS.items():
        text = text.replace(tool, label)
    return text


def parameter_keys(state):
    keys = set(state.request.parameters) | set(state.missing_parameters)
    if state.request.task_type == "new_design":
        keys |= {"beam_width_mm", "beam_depth_mm", "bar_count", "stirrup_spacing_mm"}
    return [key for key in FIELDS if key in keys] + sorted(keys - set(FIELDS))


def parameter_rows(state):
    rows = []
    for index, key in enumerate(parameter_keys(state), 1):
        item = state.request.parameters.get(key)
        group = FIELDS.get(key, (key, "其他"))[1]
        if item:
            raw = parameter_value(key, item.raw_value if item.raw_value is not None else item.value,
                                  item.raw_unit if item.raw_unit is not None else item.unit, raw=True)
            rows.append([str(index), group, field_label(key), raw,
                         parameter_value(key, item.value, item.unit), SOURCES.get(item.source, item.source),
                         "已确认" if item.confirmed else "待确认"])
        else:
            missing = key in state.missing_parameters
            derived = state.candidate.get(key)
            if derived is None:
                for tool in ("section_sizing", "flexural_design", "shear_design"):
                    result = state.tool_results.get("design." + tool)
                    if result and result.status == "success" and key in result.outputs:
                        derived = result.outputs[key]
                        break
            text = "缺失，需补充" if missing else "由设计工具确定"
            status = "缺失" if missing else "待计算"
            if derived is not None and not missing:
                text = parameter_value(key, derived, "mm" if key.endswith("_mm") else None)
                status = "已计算"
            rows.append([str(index), group, field_label(key), "—", text, "用户需提供" if missing else "计算工具", status])
    return rows


def table(headers, rows, markdown=False):
    rows = [[plain(c) for c in row] for row in rows]
    headers = [plain(c) for c in headers]
    if markdown:
        def cell(c):
            return c.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "\\|")
        return "\n".join(["| " + " | ".join(map(cell, headers)) + " |",
                          "| " + " | ".join("---" for _ in headers) + " |"] +
                         ["| " + " | ".join(map(cell, row)) + " |" for row in rows])
    def width(s):
        return sum(0 if unicodedata.combining(c) else 2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)
    widths = [min(24, max(width(row[i]) for row in [headers] + rows)) for i in range(len(headers))]
    def line(row):
        return " | ".join(s + " " * (w - width(s)) for s, w in zip(row, widths))
    def wrap(cell, limit):
        parts, current = [], ""
        for character in cell:
            if current and width(current + character) > limit:
                parts.append(current)
                current = ""
            current += character
        return parts + [current]
    def wrapped_lines(row):
        cells = [wrap(cell, limit) for cell, limit in zip(row, widths)]
        return [line([cell[i] if i < len(cell) else "" for cell in cells])
                for i in range(max(map(len, cells)))]
    rendered = wrapped_lines(headers) + ["-+-".join("-" * w for w in widths)]
    for row in rows:
        rendered += wrapped_lines(row)
    return "\n".join(rendered)


PARAMETER_HEADERS = ["编号", "类别", "参数", "提取值/输入值", "计算采用值", "来源", "状态"]


def progress_text(event: ProgressEvent) -> str:
    phase = PHASES[event.phase]
    label = TOOLS.get(event.name, event.name)
    if event.kind == "planning":
        return f"[{phase}计划] " + {"running": "正在组织工具…", "success": "计划已校验", "failed": "计划失败"}.get(event.status, event.status)
    status = {"running": "执行中", "success": "完成", "failed": "执行失败", "blocked": "上游阻断"}[event.status]
    checked = event.outputs.get("pass")
    if checked is not None and event.status == "success":
        status += "；验算通过" if checked else "；验算不通过"
    key = next((k for k in ("capacity_kn_m", "capacity_kn", "crack_width_mm", "deflection_mm", "bar_count", "stirrup_spacing_mm") if k in event.outputs), None)
    if key:
        status += "；" + OUTPUTS[key] + "=" + number(event.outputs[key], 3)
    notes = "；".join(friendly_message(e) for e in event.errors + event.warnings)
    return f"[{phase} {event.step}/{event.total_steps}] {label}：{status}" + ("；" + notes if notes else "")



LABELS = {**TOOLS, **TARGETS}

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
    lines += ['搜索直径目录：'+str(state.request.search_diameters_mm or '固定输入直径')+'；期望通过候选数：'+str(state.request.solution_count),'',
              '搜索停止原因：'+(state.search_stop_reason or '未开展设计搜索'),'']
    if state.design_alternatives:
        lines += ['## 已通过候选对照','',table(['修订','实配纵筋','纵筋面积/mm²','当前选用'],
            [[str(r['revision']),str(r['candidate']['bar_count'])+'Φ'+number(r['candidate']['bar_diameter_mm']),number(r['candidate']['As_mm2'],4),'是' if r['revision']==state.design_revision else '否'] for r in state.design_alternatives],markdown=True),
            '推荐只比较已通过候选的纵筋面积，不代表造价最优。全部候选与失败尝试保存在JSON修订记录。','']
    if json_filename: lines += [f'[完整JSON轨迹]({json_filename})','']
    if state.request.user_query: lines += ['原始需求：'+state.request.user_query,'']
    lines += ['## 分项计算过程','']
    for key,result in state.tool_results.items():
        phase,name=key.split('.',1)
        check = '通过' if result.outputs.get('pass') is True else '不通过' if result.outputs.get('pass') is False else '计算完成'
        if result.status!='success': check='执行失败' if result.status=='failed' else '上游阻断'
        lines += [f'### {"设计" if phase=="design" else "独立验算"} · {LABELS.get(name,name)} · {check}','']
        from .calculation_trace import calculation_steps
        steps=result.calculation_steps or calculation_steps(result)
        lines += [table(['步骤','计算内容','公式','数值代入','结果','单位','判定'],
            [[str(r['step']),r['title'],r['formula'],r['substitution'],number(r['result'],6) if isinstance(r['result'],(float,int)) else str(r['result']),r['unit'],('通过' if r['passed'] else '不通过') if r['passed'] is not None else '—'] for r in steps],markdown=True),'']
        rows=[]
        for k,v in result.outputs.items():
            if k in ('pass','reasons','assumptions','engineering_failure'): continue
            rows.append([OUTPUTS.get(k,k),number(v,4) if isinstance(v,(int,float)) else '未提供/不适用' if v is None else str(v)])
        lines += [table(['项目','结果'],rows,markdown=True),'']
        formal=professional_references(result.code_refs)
        if formal:lines += ['规范依据：'+'；'.join(formal),'']
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
    lines += ['- 本次未请求：'+LABELS.get(x.split('：',1)[1],x.split('：',1)[1])
              if x.startswith('本次未请求：') else '- '+x for x in state.evaluation.unimplemented]
    lines += ['- '+e for e in state.errors]
    lines += ['','## 公式与输入追溯','',table(['工具','公式版本','输入哈希'],
        [[k,r.formula_version,r.inputs_hash] for k,r in state.tool_results.items()],markdown=True),'',
        '条文、物理页与适用条件见 docs/rc_beam_cn_design_spec.md；完整精度和历史工具记录见JSON。','']
    return '\n'.join(lines)


def ALL_LABELS():
    return {**LABELS,**{k:v[0] for k,v in FIELDS.items()}}


def save_reports(state: EngineeringState, directory: str | Path) -> tuple[Path, Path]:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    stem = "beam_" + uuid4().hex[:12]
    md, data = directory / (stem + ".md"), directory / (stem + ".json")
    md.write_text(markdown_report(state, data.name), encoding="utf-8")
    data.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    return md.resolve(), data.resolve()
