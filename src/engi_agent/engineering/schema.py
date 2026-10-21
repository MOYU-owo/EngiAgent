"""Validated public contracts. All normalized engineering numbers use metric units."""
from __future__ import annotations

import math
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class ParameterValue(Contract):
    value: float | str | bool
    unit: str | None = None
    source: Literal["user", "llm_extracted", "tool", "derived", "default_confirmed"] = "user"
    confirmed: bool = False
    raw_value: float | str | bool | None = None
    raw_unit: str | None = None
    revision: int = 1


Target = Literal["flexure", "shear", "elastic_deflection"]


class TaskRequest(Contract):
    task_type: Literal["new_design", "evaluate_existing", "unsupported"]
    parameters: dict[str, ParameterValue] = Field(default_factory=dict)
    targets: list[Target] = Field(default_factory=lambda: ["flexure", "shear", "elastic_deflection"])
    user_query: str = ""
    clarification: list[str] = Field(default_factory=list)

    @field_validator("targets")
    @classmethod
    def targets_not_empty(cls, value):
        if not value or len(value) != len(set(value)):
            raise ValueError("验算目标不能为空或重复")
        return value


class TeachingProfile(Contract):
    # Explicitly included in the confirmation payload, never supplied by the LLM.
    version: Literal["teaching-rc-1"] = "teaching-rc-1"
    gamma_dead_only: float = Field(default=1.4, gt=0, le=3)
    gamma_dead: float = Field(default=1.2, gt=0, le=3)
    gamma_live: float = Field(default=1.6, gt=0, le=3)
    phi_flexure: float = Field(default=0.9, gt=0, le=1)
    phi_shear: float = Field(default=0.75, gt=0, le=1)
    stress_block_alpha: float = Field(default=0.85, gt=0, le=1)
    ultimate_concrete_strain: float = Field(default=0.003, gt=0, le=0.01)
    tension_strain_min: float = Field(default=0.005, gt=0, le=0.1)
    source: str = "StructurePoint 2021 / ACI 318-14 示例的教学子集；非完整规范实现"


class BeamParameters(Contract):
    support_type: Literal["simply_supported"]
    load_case: Literal["full_span_udl"]
    section_type: Literal["rectangular"]
    reinforcement_layers: Literal[1]
    span_mm: float = Field(gt=0)
    fc_mpa: float = Field(ge=17, le=55)
    fy_mpa: float = Field(gt=0, le=600)
    beam_width_mm: float | None = Field(default=None, gt=0)
    beam_depth_mm: float | None = Field(default=None, gt=0)
    max_width_mm: float | None = Field(default=None, gt=0)
    max_depth_mm: float | None = Field(default=None, gt=0)
    cover_mm: float = Field(gt=0)
    bar_diameter_mm: float = Field(gt=0)
    bar_area_mm2: float | None = Field(default=None, gt=0)
    bar_count: int | None = Field(default=None, ge=2, strict=True)
    stirrup_diameter_mm: float = Field(gt=0)
    stirrup_area_mm2: float | None = Field(default=None, gt=0)
    aggregate_size_mm: float = Field(gt=0)
    dead_load_kn_m: float = Field(ge=0)
    live_load_kn_m: float = Field(ge=0)
    self_weight_mode: Literal["included", "excluded", "ignore"]
    concrete_unit_weight_kn_m3: float | None = Field(default=None, gt=0)
    stirrup_fy_mpa: float | None = Field(default=None, gt=0, le=600)
    stirrup_legs: int | None = Field(default=None, ge=2, le=8, strict=True)
    stirrup_spacing_mm: float | None = Field(default=None, gt=0)
    elastic_modulus_mpa: float | None = Field(default=None, gt=0)
    deflection_limit_ratio: float | None = Field(default=None, gt=0)
    shear_position_mm: float | None = Field(default=None, ge=0)

    @model_validator(mode="before")
    @classmethod
    def reject_bool_numbers(cls, values):
        for key, value in values.items():
            if isinstance(value, bool):
                raise ValueError(f"{key}: 布尔值不能当数值使用")
        return values


UNITS = {name: ("mm" if name.endswith("_mm") else "mm2" if name.endswith("_mm2")
                else "MPa" if name.endswith("_mpa") else "kN/m" if name.endswith("_kn_m")
                else "kN/m3" if name.endswith("_kn_m3") else None)
         for name in BeamParameters.model_fields}
FACTORS = {
    "mm": {"mm": 1, "m": 1000, "cm": 10, "in": 25.4, "ft": 304.8},
    "mm2": {"mm2": 1, "cm2": 100, "in2": 645.16},
    "MPa": {"MPa": 1, "GPa": 1000, "psi": 0.006894757293168, "ksi": 6.894757293168},
    "kN/m": {"kN/m": 1, "N/mm": 1, "N/m": 0.001, "kip/ft": 14.593902937206},
    "kN/m3": {"kN/m3": 1, "N/m3": 0.001, "lb/ft3": 0.157087463846},
}


def normalize(request: TaskRequest) -> TaskRequest:
    result = request.model_copy(deep=True)
    for name, item in result.parameters.items():
        if name not in UNITS:
            raise ValueError(f"未知参数: {name}")
        expected = UNITS[name]
        item.raw_value = item.value if item.raw_value is None else item.raw_value
        item.raw_unit = item.unit if item.raw_unit is None else item.raw_unit
        if expected:
            if item.unit not in FACTORS[expected]:
                raise ValueError(f"{name}: 单位 {item.unit!r} 不匹配 {expected}")
            if isinstance(item.value, bool):
                raise ValueError(f"{name}: 布尔值不能当数值")
            item.value = float(item.value) * FACTORS[expected][item.unit]
            if not math.isfinite(item.value):
                raise ValueError(f"{name}: 必须为有限数值")
            item.unit = expected
        elif item.unit not in (None, "", "1"):
            raise ValueError(f"{name}: 无量纲/枚举字段不得带单位")
        if name in {"bar_count", "stirrup_legs", "reinforcement_layers"}:
            if isinstance(item.value, bool) or float(item.value) != int(float(item.value)):
                raise ValueError(f"{name}: 必须为整数")
            item.value = str(int(float(item.value)))  # ParameterValue preserves exact integer text.
    # Validate all supplied fields now, even if other required fields are absent.
    from pydantic import TypeAdapter
    for name, item in result.parameters.items():
        field = BeamParameters.model_fields[name]
        TypeAdapter(field.rebuild_annotation()).validate_python(parameter_python(name, item))
    return result


def parameter_python(name: str, item: ParameterValue):
    return int(item.value) if name in {"bar_count", "stirrup_legs", "reinforcement_layers"} else item.value


def required_fields(request: TaskRequest) -> set[str]:
    required = {name for name, f in BeamParameters.model_fields.items() if f.is_required()}
    if request.task_type == "evaluate_existing":
        required |= {"beam_width_mm", "beam_depth_mm", "bar_count"}
    if "shear" in request.targets or request.task_type == "new_design":
        required |= {"stirrup_fy_mpa", "stirrup_legs"}
        if request.task_type == "evaluate_existing":
            required.add("stirrup_spacing_mm")
    if "elastic_deflection" in request.targets:
        required |= {"elastic_modulus_mpa", "deflection_limit_ratio"}
    mode = request.parameters.get("self_weight_mode")
    if mode and mode.value == "excluded":
        required.add("concrete_unit_weight_kn_m3")
    return required


def missing_fields(request: TaskRequest) -> list[str]:
    return sorted(name for name in required_fields(request)
                  if name not in request.parameters)


class ToolResult(Contract):
    tool: str
    status: Literal["success", "failed", "blocked"]
    inputs_hash: str
    inputs: dict[str, Any]
    outputs: dict[str, Any] = Field(default_factory=dict)
    code_refs: list[str] = Field(default_factory=lambda: ["docs/engineering_tools.md / teaching-rc-1"])
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    revision: int = 1
    formula_version: str = "teaching-rc-1"


class EvaluationResult(Contract):
    status: Literal["pass", "fail", "incomplete", "error"] = "incomplete"
    checks: dict[str, bool] = Field(default_factory=dict)
    code_status: Literal["未完成"] = "未完成"
    overall_status: Literal["incomplete"] = "incomplete"
    unimplemented: list[str] = Field(default_factory=lambda: ["中国规范核验", "开裂与长期挠度", "裂缝", "锚固、搭接、耐久性和完整构造"])


class ProgressEvent(Contract):
    """Structured progress for terminal display and future UI consumers."""
    phase: Literal["design", "evaluation"]
    kind: Literal["planning", "tool"]
    name: str
    status: Literal["running", "success", "failed", "blocked"]
    step: int = 0
    total_steps: int = 0
    outputs: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class EngineeringState(Contract):
    request: TaskRequest
    profile: TeachingProfile = Field(default_factory=TeachingProfile)
    confirmed: bool = False
    confirmation_hash: str | None = None
    design_revision: int = 1
    execution_plan: list[str] = Field(default_factory=list)
    tool_results: dict[str, ToolResult] = Field(default_factory=dict)
    candidate: dict[str, Any] = Field(default_factory=dict)
    evaluation: EvaluationResult = Field(default_factory=EvaluationResult)
    errors: list[str] = Field(default_factory=list)
    role_events: list[dict[str, Any]] = Field(default_factory=list)
    missing_parameters: list[str] = Field(default_factory=list)
    progress_events: list[ProgressEvent] = Field(default_factory=list)
    presentation_warnings: list[str] = Field(default_factory=list)
