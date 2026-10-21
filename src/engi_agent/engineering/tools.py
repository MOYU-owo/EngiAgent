"""Whitelisted deterministic functions; N/mm/MPa within section equations."""
from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable
from .schema import BeamParameters, TeachingProfile, ToolResult
from .outputs import OUTPUT_MODELS

PSI_PER_MPA = 145.03773773


class EngineeringFailure(ValueError):
    """A valid computation found an infeasible teaching-model design."""


def section_sizing(p: BeamParameters, profile: TeachingProfile, prior: dict) -> dict:
    h = p.beam_depth_mm or math.ceil(p.span_mm / 16 / 25) * 25
    b = p.beam_width_mm or math.ceil(0.6 * h / 25) * 25
    if (p.max_depth_mm and h > p.max_depth_mm) or (p.max_width_mm and b > p.max_width_mm):
        raise EngineeringFailure("截面尺寸超过用户约束；未自动改变约束或增大截面")
    return {"beam_width_mm": b, "beam_depth_mm": h,
            "sizing_basis": "已有尺寸保留；缺失尺寸采用L/16、b=0.6h及25mm取整的教学初选"}


def section_geometry(p: BeamParameters, profile: TeachingProfile, prior: dict) -> dict:
    section = prior["section_sizing"]
    b, h = section["beam_width_mm"], section["beam_depth_mm"]
    d = h - p.cover_mm - p.stirrup_diameter_mm - p.bar_diameter_mm / 2
    if d <= 0 or b <= 2 * (p.cover_mm + p.stirrup_diameter_mm) + p.bar_diameter_mm:
        raise EngineeringFailure("保护层及钢筋尺寸与截面冲突，有效高度或净宽不足")
    return {"beam_width_mm": b, "beam_depth_mm": h, "effective_depth_mm": d,
            "gross_inertia_mm4": b * h**3 / 12,
            "bar_area_mm2": p.bar_area_mm2 or math.pi * p.bar_diameter_mm**2 / 4,
            "stirrup_area_mm2": p.stirrup_area_mm2 or math.pi * p.stirrup_diameter_mm**2 / 4}


def load_combination(p: BeamParameters, profile: TeachingProfile, prior: dict) -> dict:
    g = prior["section_geometry"]
    sw = (p.concrete_unit_weight_kn_m3 or 0) * g["beam_width_mm"] * g["beam_depth_mm"] / 1e6
    if p.self_weight_mode == "excluded" and p.concrete_unit_weight_kn_m3 is None:
        raise ValueError("计入自重需要混凝土容重")
    dead = p.dead_load_kn_m + (sw if p.self_weight_mode == "excluded" else 0)
    combinations = {"dead_only": profile.gamma_dead_only * dead,
                    "dead_live": profile.gamma_dead * dead + profile.gamma_live * p.live_load_kn_m}
    governing = max(combinations, key=combinations.get)
    return {"self_weight_kn_m": sw if p.concrete_unit_weight_kn_m3 else None,
            "self_weight_mode": p.self_weight_mode, "total_dead_load_kn_m": dead,
            "strength_combinations_kn_m": combinations, "governing_combination": governing,
            "ultimate_load_kn_m": combinations[governing],
            "service_load_kn_m": dead + p.live_load_kn_m}


def beam_analysis(p: BeamParameters, profile: TeachingProfile, prior: dict) -> dict:
    loads, g = prior["load_combination"], prior["section_geometry"]
    span = p.span_mm / 1000
    # The simplified model uses the section at d from the support. Both this and
    # the support maximum are reported so consumers cannot silently mix demands.
    x = p.shear_position_mm if p.shear_position_mm is not None else g["effective_depth_mm"]
    if not 0 <= x <= p.span_mm:
        raise EngineeringFailure("剪力计算位置不在梁跨内")
    if g["effective_depth_mm"] >= p.span_mm / 2:
        raise EngineeringFailure("梁跨过短，不能采用本简化梁模型")
    w, ws = loads["ultimate_load_kn_m"], loads["service_load_kn_m"]
    return {"Mu_kn_m": w * span**2 / 8, "Vu_max_kn": w * span / 2,
            "reaction_left_kn": w * span / 2, "reaction_right_kn": w * span / 2,
            "shear_position_mm": x, "Vu_at_position_kn": w * (span / 2 - x / 1000),
            "critical_shear_position_mm": g["effective_depth_mm"],
            "Vu_design_kn": w * (span / 2 - g["effective_depth_mm"] / 1000),
            "service_moment_kn_m": ws * span**2 / 8,
            "service_shear_kn": ws * span / 2}


def minimum_steel(p: BeamParameters, g: dict) -> float:
    return max(3 / math.sqrt(PSI_PER_MPA) * math.sqrt(p.fc_mpa), 200 / PSI_PER_MPA) / p.fy_mpa * g["beam_width_mm"] * g["effective_depth_mm"]


def flexural_capacity(p: BeamParameters, profile: TeachingProfile, g: dict, count: int) -> dict:
    area = count * g["bar_area_mm2"]
    b, d = g["beam_width_mm"], g["effective_depth_mm"]
    a = area * p.fy_mpa / (profile.stress_block_alpha * p.fc_mpa * b)
    beta = min(0.85, max(0.65, 0.85 - 0.05 * (p.fc_mpa * PSI_PER_MPA - 4000) / 1000))
    c = a / beta
    strain = profile.ultimate_concrete_strain * (d - c) / c
    return {"As_mm2": area, "compression_block_mm": a, "neutral_axis_mm": c,
            "beta1": beta, "tension_strain": strain,
            "tension_controlled": strain >= profile.tension_strain_min and a < d,
            "capacity_kn_m": profile.phi_flexure * area * p.fy_mpa * (d - a / 2) / 1e6,
            "minimum_steel_mm2": minimum_steel(p, g)}


def layout(p: BeamParameters, g: dict, count: int) -> dict:
    if count < 2:
        raise EngineeringFailure("单层示范要求至少两根纵筋")
    center = (g["beam_width_mm"] - 2 * (p.cover_mm + p.stirrup_diameter_mm) - p.bar_diameter_mm) / (count - 1)
    clear = center - p.bar_diameter_mm
    minimum = max(p.bar_diameter_mm, 25.4, 4 * p.aggregate_size_mm / 3)
    fs = 2 * p.fy_mpa / 3
    maximum = min(380 * 280 / fs - 2.5 * p.cover_mm, 300 * 280 / fs)
    reasons = []
    if clear < minimum:
        reasons.append("纵筋净距小于教学最小净距，单层布置不可行")
    if center > maximum:
        reasons.append("纵筋中心距超过教学最大间距")
    return {"center_spacing_mm": center, "clear_spacing_mm": clear,
            "minimum_clear_spacing_mm": minimum, "maximum_center_spacing_mm": maximum,
            "pass": not reasons, "reasons": reasons}


def flexural_design(p: BeamParameters, profile: TeachingProfile, prior: dict) -> dict:
    g = prior["section_geometry"]
    mu = prior["beam_analysis"]["Mu_kn_m"] * 1e6
    b, d = g["beam_width_mm"], g["effective_depth_mm"]
    # Solve in tension force T to avoid an iterative LLM-based area calculation.
    k = profile.stress_block_alpha * p.fc_mpa * b
    disc = d*d - 2 * mu / (profile.phi_flexure * k)
    if disc <= 0:
        raise EngineeringFailure("初始截面无法承受设计弯矩")
    # Rationalized smaller root avoids cancellation for tiny demand.
    force = (2 * mu / profile.phi_flexure) / (d + math.sqrt(disc))
    required = max(force / p.fy_mpa, minimum_steel(p, g))
    count = max(2, math.ceil(required / g["bar_area_mm2"]))
    capacity = flexural_capacity(p, profile, g, count)
    arrangement = layout(p, g, count)
    if not capacity["tension_controlled"]:
        raise EngineeringFailure("候选配筋不满足受拉控制教学模型，需人工调整截面")
    if not arrangement["pass"]:
        raise EngineeringFailure("候选纵筋单层布置间距不满足教学条件，未自动改设")
    return {"required_steel_mm2": required, "bar_count": count,
            "bar_diameter_mm": p.bar_diameter_mm, **capacity, "layout": arrangement}


def shear_terms(p: BeamParameters, profile: TeachingProfile, prior: dict) -> dict:
    g = prior["section_geometry"]
    if p.stirrup_fy_mpa is None or p.stirrup_legs is None:
        raise ValueError("缺少箍筋强度或肢数")
    b, d = g["beam_width_mm"], g["effective_depth_mm"]
    root = math.sqrt(p.fc_mpa) * b * d / math.sqrt(PSI_PER_MPA)
    vc = 2 * root
    demand = prior["beam_analysis"]["Vu_design_kn"] * 1000
    vs = max(0, demand / profile.phi_shear - vc)
    minimum = max(0.75 / math.sqrt(PSI_PER_MPA) * math.sqrt(p.fc_mpa) * b / p.stirrup_fy_mpa,
                  50 / PSI_PER_MPA * b / p.stirrup_fy_mpa)
    maximum = min(d / 2, 609.6) if vs <= 4 * root else min(d / 4, 304.8)
    return {"concrete_capacity_n": vc, "required_stirrup_strength_n": vs,
            "maximum_stirrup_strength_n": 8 * root,
            "minimum_av_over_s": minimum, "maximum_spacing_mm": maximum,
            "Av_mm2": p.stirrup_legs * g["stirrup_area_mm2"],
            "demand_kn": demand / 1000}


def shear_design(p: BeamParameters, profile: TeachingProfile, prior: dict) -> dict:
    terms = shear_terms(p, profile, prior)
    d = prior["section_geometry"]["effective_depth_mm"]
    vs = terms["required_stirrup_strength_n"]
    if vs > terms["maximum_stirrup_strength_n"]:
        raise EngineeringFailure("剪力超过教学模型截面上限，需人工调整截面")
    ratio = max(terms["minimum_av_over_s"], vs / (p.stirrup_fy_mpa * d))
    spacing = math.floor(min(terms["Av_mm2"] / ratio, terms["maximum_spacing_mm"]) / 5) * 5
    if spacing <= 0:
        raise EngineeringFailure("无正可行箍筋间距")
    return {**terms, "stirrup_spacing_mm": spacing, "stirrup_legs": p.stirrup_legs,
            "stirrup_diameter_mm": p.stirrup_diameter_mm,
            "arrangement": "全跨均布；首轮不输出分区截断点或箍筋总数"}


def flexural_check(p: BeamParameters, profile: TeachingProfile, prior: dict) -> dict:
    if p.bar_count is None:
        raise ValueError("既有梁验算缺少实配纵筋根数")
    cap = flexural_capacity(p, profile, prior["section_geometry"], p.bar_count)
    demand = prior["beam_analysis"]["Mu_kn_m"]
    reasons = []
    if not cap["tension_controlled"]:
        reasons.append("不满足受拉控制教学模型，不能采用当前抗弯折减系数")
    if cap["As_mm2"] < cap["minimum_steel_mm2"]:
        reasons.append("实配纵筋面积低于教学最小配筋量")
    if cap["capacity_kn_m"] < demand:
        reasons.append("抗弯承载力低于设计弯矩")
    return {**cap, "demand_kn_m": demand,
            "pass": not reasons, "reasons": reasons}


def detailing_check(p: BeamParameters, profile: TeachingProfile, prior: dict) -> dict:
    return layout(p, prior["section_geometry"], p.bar_count)


def shear_check(p: BeamParameters, profile: TeachingProfile, prior: dict) -> dict:
    if p.stirrup_spacing_mm is None:
        raise ValueError("既有梁验算缺少箍筋间距")
    terms = shear_terms(p, profile, prior)
    d = prior["section_geometry"]["effective_depth_mm"]
    ratio = terms["Av_mm2"] / p.stirrup_spacing_mm
    actual_vs = ratio * p.stirrup_fy_mpa * d
    capacity = profile.phi_shear * (terms["concrete_capacity_n"] + actual_vs) / 1000
    reasons = []
    if capacity < terms["demand_kn"]:
        reasons.append("抗剪承载力低于临界截面设计剪力")
    if ratio < terms["minimum_av_over_s"]:
        reasons.append("箍筋量低于教学最小配箍量")
    if actual_vs > terms["maximum_stirrup_strength_n"]:
        reasons.append("箍筋贡献超过教学模型截面上限")
    if p.stirrup_spacing_mm > terms["maximum_spacing_mm"]:
        reasons.append("箍筋间距超过教学最大间距")
    return {**terms, "capacity_kn": capacity, "provided_stirrup_strength_n": actual_vs,
            "pass": not reasons, "reasons": reasons}


def elastic_deflection(p: BeamParameters, profile: TeachingProfile, prior: dict) -> dict:
    if p.elastic_modulus_mpa is None or p.deflection_limit_ratio is None:
        raise ValueError("弹性挠度需要确认弹性模量及限值分母")
    inertia = prior["section_geometry"]["gross_inertia_mm4"]
    w = prior["load_combination"]["service_load_kn_m"]
    delta = 5 * w * p.span_mm**4 / (384 * p.elastic_modulus_mpa * inertia)
    limit = p.span_mm / p.deflection_limit_ratio
    return {"deflection_mm": delta, "limit_mm": limit, "gross_inertia_mm4": inertia,
            "service_load_kn_m": w, "pass": delta <= limit,
            "reasons": [] if delta <= limit else ["毛截面弹性挠度超过确认的教学限值"],
            "model": "毛截面弹性挠度，不含开裂、徐变或收缩"}


REGISTRY: dict[str, Callable] = {fn.__name__: fn for fn in (
    section_sizing, section_geometry, load_combination, beam_analysis,
    flexural_design, shear_design, flexural_check, detailing_check, shear_check, elastic_deflection)}


def execute_tool(name: str, p: BeamParameters, profile: TeachingProfile, prior: dict) -> ToolResult:
    inputs = {"parameters": p.model_dump(), "profile": profile.model_dump(), "upstream": prior}
    digest = hashlib.sha256(json.dumps(inputs, sort_keys=True, allow_nan=False).encode()).hexdigest()
    result = ToolResult(tool=name, status="success", inputs_hash=digest, inputs=inputs)
    if p.self_weight_mode == "ignore":
        result.warnings.append("本案例明确忽略梁自重，仅作参考对照")
    try:
        if name not in REGISTRY:
            raise ValueError(f"工具不在白名单: {name}")
        result.outputs = OUTPUT_MODELS[name].model_validate(REGISTRY[name](p, profile, prior)).model_dump(by_alias=True)
        json.dumps(result.outputs, allow_nan=False)  # Reject overflow/non-finite output.
    except EngineeringFailure as exc:
        result.status = "failed"
        result.errors = [str(exc)]
        result.outputs = {"pass": False, "engineering_failure": True}
    except Exception as exc:
        result.status = "failed"
        result.errors = [f"{type(exc).__name__}: 工具执行异常"]
    return result
