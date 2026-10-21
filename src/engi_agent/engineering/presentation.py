"""Deterministic Chinese engineering views shared by terminal and Markdown.

Formatting is display-only: full precision remains in state/JSON and checks are
never recomputed from rounded display values.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import re
import unicodedata
from .schema import EngineeringState, ProgressEvent


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
    "fc_mpa": ("混凝土圆柱抗压强度", "材料"),
    "elastic_modulus_mpa": ("混凝土弹性模量", "材料"),
    "concrete_unit_weight_kn_m3": ("混凝土容重", "材料"),
    "fy_mpa": ("纵筋屈服强度", "纵筋"),
    "bar_diameter_mm": ("纵筋直径", "纵筋"),
    "bar_area_mm2": ("单根纵筋公称面积", "纵筋"),
    "bar_count": ("纵筋根数", "纵筋"),
    "reinforcement_layers": ("受拉纵筋层数", "纵筋"),
    "stirrup_fy_mpa": ("箍筋屈服强度", "箍筋"),
    "stirrup_diameter_mm": ("箍筋直径", "箍筋"),
    "stirrup_area_mm2": ("单肢箍筋公称面积", "箍筋"),
    "stirrup_legs": ("箍筋肢数", "箍筋"),
    "stirrup_spacing_mm": ("箍筋间距", "箍筋"),
    "aggregate_size_mm": ("最大骨料粒径", "布置"),
    "dead_load_kn_m": ("输入恒载", "荷载"),
    "live_load_kn_m": ("活载", "荷载"),
    "self_weight_mode": ("自重约定", "荷载"),
    "shear_position_mm": ("剪力查询位置", "分析"),
    "deflection_limit_ratio": ("挠度限值分母", "正常使用"),
}
FIELD_ALIASES = {label: key for key, (label, _) in FIELDS.items()}
FIELD_ALIASES.update({"梁跨度": "span_mm", "保护层": "cover_mm", "钢筋根数": "bar_count"})
FIELD_ALIASES.update({"恒载": "dead_load_kn_m", "活荷载": "live_load_kn_m"})
ENUMS = {
    "simply_supported": "简支", "rectangular": "矩形", "full_span_udl": "全跨均布",
    "included": "输入恒载已含自重，不重复计入",
    "excluded": "输入恒载不含自重，程序另行计入",
    "ignore": "明确忽略自重（参考对照）",
}
ENUM_INPUTS = {"简支": "simply_supported", "矩形": "rectangular", "全跨均布": "full_span_udl",
               "已含自重": "included", "另计自重": "excluded", "忽略自重": "ignore"}
SOURCES = {"user": "用户/任务文件", "llm_extracted": "模型提取", "tool": "计算工具",
           "derived": "推导", "default_confirmed": "已确认假设"}
TARGETS = {"flexure": "抗弯", "shear": "抗剪", "elastic_deflection": "简化弹性挠度"}
TOOLS = {"section_sizing": "截面初选", "section_geometry": "截面与钢筋几何",
         "load_combination": "自重与荷载组合", "beam_analysis": "内力分析",
         "flexural_design": "纵筋设计", "shear_design": "箍筋设计",
         "flexural_check": "抗弯验算", "detailing_check": "纵筋布置检查",
         "shear_check": "抗剪验算", "elastic_deflection": "简化弹性挠度验算"}
PHASES = {"design": "设计", "evaluation": "验算"}
STATUS = {"pass": "所请求项目试算通过", "fail": "试算不通过", "error": "执行错误", "incomplete": "计算未完成"}
PROFILE_FIELDS = {"gamma_dead_only": "仅恒载组合系数", "gamma_dead": "恒活载组合：恒载系数",
                  "gamma_live": "恒活载组合：活载系数", "phi_flexure": "抗弯承载力折减系数",
                  "phi_shear": "抗剪承载力折减系数", "stress_block_alpha": "应力块系数",
                  "ultimate_concrete_strain": "混凝土极限压应变", "tension_strain_min": "受拉控制应变下限"}
UNITS = {"mm2": "mm²", "kN/m3": "kN/m³", "in2": "in²", "lb/ft3": "lb/ft³"}


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


def unimplemented_labels(state):
    return ["本次未请求：" + TARGETS.get(item.split("：", 1)[1], item.split("：", 1)[1])
            if item.startswith("本次未请求：") else item for item in state.evaluation.unimplemented]


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


def profile_rows(state):
    return [[label, format(getattr(state.profile, key), ".15g")] for key, label in PROFILE_FIELDS.items()]


@dataclass(frozen=True)
class ResultView:
    label: str
    status: str
    rows: list[list[str]]
    notes: list[str]
    summary: str


def result_view(name: str, outputs: dict, status="success", errors=(), warnings=()) -> ResultView:
    """Pure view projection: no engineering calculations or new pass decisions."""
    label = TOOLS.get(name, name)
    if status != "success":
        return ResultView(label, "上游阻断，未执行" if status == "blocked" else
                          "方案不可行" if outputs.get("engineering_failure") else "执行未完成",
                          [], [friendly_message(e) for e in list(errors) + list(warnings)],
                          "; ".join(map(friendly_message, errors)) or "未得到有效结果")
    o = outputs
    rows, notes = [], list(warnings)
    def add(label, key, unit="", decimals=2):
        if key in o:
            rows.append([label, quantity(o[key], unit, decimals)])
    if name == "section_sizing":
        add("梁宽", "beam_width_mm", "mm"); add("梁高", "beam_depth_mm", "mm")
        notes.append(o.get("sizing_basis", ""))
    elif name == "section_geometry":
        add("有效高度", "effective_depth_mm", "mm"); add("毛截面惯性矩", "gross_inertia_mm4", "mm⁴")
        add("单根纵筋面积", "bar_area_mm2", "mm2"); add("单肢箍筋面积", "stirrup_area_mm2", "mm2")
    elif name == "load_combination":
        rows.append(["自重处理", ENUMS.get(o.get("self_weight_mode"), "未说明")])
        add("截面对应自重", "self_weight_kn_m", "kN/m")
        add("计算采用恒载", "total_dead_load_kn_m", "kN/m")
        for key, value in o.get("strength_combinations_kn_m", {}).items():
            rows.append([{"dead_only": "仅恒载组合", "dead_live": "恒活载组合"}.get(key, key), quantity(value, "kN/m")])
        add("承载力设计荷载", "ultimate_load_kn_m", "kN/m"); add("正常使用荷载", "service_load_kn_m", "kN/m")
    elif name == "beam_analysis":
        add("最大设计弯矩", "Mu_kn_m", "kN·m"); add("支座最大剪力", "Vu_max_kn", "kN")
        add("抗剪检查截面距支座", "critical_shear_position_mm", "mm"); add("抗剪检查设计剪力", "Vu_design_kn", "kN")
        add("查询位置距支座", "shear_position_mm", "mm"); add("查询位置剪力", "Vu_at_position_kn", "kN")
        notes.append("支座最大剪力、查询剪力与抗剪检查剪力按不同位置区分。")
    elif name in {"flexural_design", "flexural_check"}:
        add("最小配筋面积", "minimum_steel_mm2", "mm2"); add("需求配筋面积", "required_steel_mm2", "mm2")
        add("实配纵筋根数", "bar_count"); add("纵筋直径", "bar_diameter_mm", "mm")
        add("实配纵筋总面积", "As_mm2", "mm2"); add("设计弯矩需求", "demand_kn_m", "kN·m")
        add("折减后抗弯承载力", "capacity_kn_m", "kN·m")
        add("受拉钢筋应变", "tension_strain", decimals=6)
        if "tension_controlled" in o:
            rows.append(["受拉控制模型适用", "是" if o["tension_controlled"] else "否"])
        if "layout" in o:
            add_layout = o["layout"]
            rows += [["纵筋中心距", quantity(add_layout["center_spacing_mm"], "mm")],
                     ["纵筋净距", quantity(add_layout["clear_spacing_mm"], "mm")]]
    elif name in {"shear_design", "shear_check"}:
        add("抗剪设计剪力需求", "demand_kn", "kN")
        if "concrete_capacity_n" in o:
            rows.append(["混凝土名义抗剪贡献（未折减）", quantity(o["concrete_capacity_n"] / 1000, "kN")])
        if "required_stirrup_strength_n" in o:
            rows.append(["按承载力需补足的箍筋贡献", quantity(o["required_stirrup_strength_n"] / 1000, "kN")])
        add("箍筋肢数", "stirrup_legs"); add("箍筋直径", "stirrup_diameter_mm", "mm")
        add("实配箍筋间距", "stirrup_spacing_mm", "mm"); add("允许最大箍筋间距", "maximum_spacing_mm", "mm")
        add("折减后抗剪承载力", "capacity_kn", "kN")
        if o.get("required_stirrup_strength_n") == 0:
            notes.append("承载力无需箍筋额外补足，仍检查最小配箍量和最大间距。")
        if o.get("arrangement"):
            notes.append(o["arrangement"])
    elif name == "detailing_check":
        add("纵筋中心距", "center_spacing_mm", "mm"); add("允许最大中心距", "maximum_center_spacing_mm", "mm")
        add("纵筋净距", "clear_spacing_mm", "mm"); add("要求最小净距", "minimum_clear_spacing_mm", "mm")
        notes.append("仅检查当前实现的纵筋间距条件，不代表完整构造验算。")
    elif name == "elastic_deflection":
        add("正常使用荷载", "service_load_kn_m", "kN/m"); add("计算弹性挠度", "deflection_mm", "mm")
        add("确认的挠度限值", "limit_mm", "mm"); notes.append(o.get("model", ""))
    notes += o.get("reasons", [])
    conclusion = "不通过" if o.get("pass") is False else "通过" if o.get("pass") is True else "已完成计算"
    # The terminal gets key outcomes; the report keeps the full metric table.
    compact_labels = {
        "section_sizing": {"梁宽", "梁高"},
        "section_geometry": {"有效高度", "单根纵筋面积"},
        "load_combination": {"截面对应自重", "承载力设计荷载", "正常使用荷载"},
        "beam_analysis": {"最大设计弯矩", "支座最大剪力", "抗剪检查设计剪力"},
        "flexural_design": {"实配纵筋根数", "纵筋直径", "实配纵筋总面积"},
        "shear_design": {"箍筋肢数", "箍筋直径", "实配箍筋间距"},
        "flexural_check": {"设计弯矩需求", "折减后抗弯承载力"},
        "detailing_check": {"纵筋净距", "要求最小净距"},
        "shear_check": {"抗剪设计剪力需求", "折减后抗剪承载力"},
        "elastic_deflection": {"计算弹性挠度", "确认的挠度限值"},
    }
    summary = "；".join(label + " " + value for label, value in rows if label in compact_labels.get(name, set()))
    if o.get("pass") is not None:
        summary = conclusion + "；" + summary
    return ResultView(label, conclusion, rows, [plain(n) for n in notes if n], summary)


def progress_text(event: ProgressEvent) -> str:
    phase = PHASES[event.phase]
    if event.kind == "planning":
        message = {"running": "正在组织工具计划…", "success": "工具计划已确认", "failed": "工具计划失败，停止该阶段"}[event.status]
        return f"[{phase}] {message}"
    label = TOOLS.get(event.name, event.name)
    prefix = f"[{phase} {event.step}/{event.total_steps}] {label}"
    if event.status == "running":
        return prefix + "：计算中…"
    view = result_view(event.name, event.outputs, event.status, event.errors, event.warnings)
    return prefix + "：" + view.status + "\n    " + view.summary + (
        "\n    " + "；".join(view.notes) if view.notes else "")


def scheme_rows(state):
    """Use actual candidate for design, confirmed actual inputs for evaluation."""
    p = state.request.parameters
    rows = []
    for key in ("beam_width_mm", "beam_depth_mm", "bar_count", "bar_diameter_mm", "stirrup_legs", "stirrup_diameter_mm", "stirrup_spacing_mm"):
        value = state.candidate.get(key) if state.candidate else None
        # Do not present unexecuted new-design inputs as a completed candidate.
        if value is None and (state.candidate or state.request.task_type == "evaluate_existing") and key in p:
            value = p[key].value
        if value is not None:
            unit = "mm" if key.endswith("_mm") else ""
            rows.append([field_label(key), parameter_value(key, value, unit)])
    area = state.candidate.get("As_mm2")
    if area is None:
        item = state.tool_results.get("evaluation.flexural_check")
        if item and item.status == "success":
            area = item.outputs.get("As_mm2")
    if area is not None:
        rows.append(["实配纵筋总面积", quantity(area, "mm2")])
    return rows


def check_rows(state):
    """Show requested checks absent from results as not completed, never pass."""
    expected = []
    for target in state.request.targets:
        expected += {"flexure": ["flexural_check", "detailing_check"], "shear": ["shear_check"],
                     "elastic_deflection": ["elastic_deflection"]}[target]
    rows = []
    for name in expected:
        result = state.tool_results.get("evaluation." + name)
        if result is None or result.status != "success":
            rows.append([TOOLS[name], "—", "—", "未完成", "未执行或被上游阻断；不能判断通过"])
            continue
        o = result.outputs
        if name == "flexural_check":
            demand, response = quantity(o["demand_kn_m"], "kN·m"), quantity(o["capacity_kn_m"], "kN·m")
        elif name == "shear_check":
            demand, response = quantity(o["demand_kn"], "kN"), quantity(o["capacity_kn"], "kN")
        elif name == "elastic_deflection":
            demand, response = "限值 " + quantity(o["limit_mm"], "mm"), "挠度 " + quantity(o["deflection_mm"], "mm")
        else:
            demand = "净距 ≥ " + quantity(o["minimum_clear_spacing_mm"], "mm") + "；中心距 ≤ " + quantity(o["maximum_center_spacing_mm"], "mm")
            response = "净距 " + quantity(o["clear_spacing_mm"], "mm") + "；中心距 " + quantity(o["center_spacing_mm"], "mm")
        rows.append([TOOLS[name], demand, response, "通过" if o["pass"] else "不通过",
                     "；".join(o.get("reasons", [])) or "当前教学模型内通过"])
    return rows


CHECK_HEADERS = ["验算项目", "需求/限值", "能力/计算响应", "结论", "说明"]


def result_overview(state, markdown=False):
    task = "新梁设计" if state.request.task_type == "new_design" else "已有梁独立验算" if state.request.task_type == "evaluate_existing" else "不支持的任务"
    lines = [f"任务：{task}；本次结果：{STATUS[state.evaluation.status]}",
             "中国规范核验：未完成；完整工程合规：未完成。"]
    scheme = scheme_rows(state)
    lines += ["", "设计方案" if state.request.task_type == "new_design" else "本次验算的已有方案", ""]
    lines.append(table(["项目", "数值"], scheme, markdown) if scheme else "未形成有效设计方案。")
    rows = check_rows(state) if state.request.task_type != "unsupported" else []
    if rows:
        lines += ["", "验算对比", "", table(CHECK_HEADERS, rows, markdown)]
    if state.candidate and state.evaluation.status == "error":
        lines.append("已生成候选，但复核执行出错，不能认定方案通过。")
    elif state.candidate and state.evaluation.status == "fail":
        lines.append("候选未通过全部所请求检查，需人工调整后重新运行。")
    return "\n".join(lines)
