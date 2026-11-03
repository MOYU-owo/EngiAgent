"""Input boundary for the deliberately small Chinese-code beam implementation."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)


class CNProfile(Contract):
    version: Literal['cn-rc-2024-v1'] = 'cn-rc-2024-v1'
    source: str = 'GB/T 50010-2010（2024修订+2015未修订条文）；GB 55001-2021；GB 55008-2021；GB 50009-2012'
    gamma_dead: Literal[1.3] = 1.3
    gamma_live: Literal[1.5] = 1.5
    source_note: str = '普通房屋、50年、二级安全、单一不利重力可变作用；不含抗震专项'


# Explicit project catalogue, not a claim that all other products are prohibited by law.
REBAR_DIAMETERS = (6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40, 50)
DIAMETER_FIELDS = {'bar_diameter_mm', 'stirrup_diameter_mm', 'top_bar_diameter_mm', 'side_bar_diameter_mm'}


def validate_diameter(name, value, grade=None):
    allowed = REBAR_DIAMETERS[:10] if grade == 'HPB300' else REBAR_DIAMETERS
    if name == 'side_bar_diameter_mm' and value == 0:
        return value
    if value not in allowed:
        raise ValueError(f'{name}={value}mm不在程序支持的公称直径目录中：{allowed}；不接受任意直径或自动取整')
    return value


class CNParameters(Contract):
    support_type: Literal['simply_supported']
    load_case: Literal['full_span_udl']
    section_type: Literal['rectangular']
    reinforcement_layers: Literal[1]
    span_mm: float = Field(gt=0)
    concrete_grade: Literal['C25', 'C30', 'C35', 'C40', 'C45', 'C50']
    steel_grade: Literal['HRB400', 'HRB500']
    stirrup_grade: Literal['HPB300', 'HRB400', 'HRB500']
    beam_width_mm: float | None = Field(default=None, gt=0)
    beam_depth_mm: float | None = Field(default=None, gt=0)
    max_width_mm: float | None = Field(default=None, gt=0)
    max_depth_mm: float | None = Field(default=None, gt=0)
    cover_mm: float = Field(ge=20)
    bar_diameter_mm: float = Field(gt=0)
    bar_count: int | None = Field(default=None, ge=2, strict=True)
    stirrup_diameter_mm: float = Field(ge=6)
    stirrup_legs: int = Field(ge=2, le=4, strict=True)
    stirrup_spacing_mm: float | None = Field(default=None, gt=0)
    aggregate_size_mm: float = Field(gt=0)
    dead_load_kn_m: float | None = Field(default=None, ge=0)
    live_load_kn_m: float | None = Field(default=None, ge=0)
    self_weight_mode: Literal['included', 'excluded']
    concrete_unit_weight_kn_m3: float = Field(gt=0)
    design_moment_kn_m: float | None = Field(default=None, ge=0)
    design_shear_kn: float | None = Field(default=None, ge=0)
    live_quasi_factor: float = Field(ge=0, le=1)
    live_combination_factor: float = Field(ge=0, le=1)
    live_frequency_factor: float = Field(ge=0, le=1)
    importance_factor: Literal[1.0] = 1.0
    design_life_years: Literal[50] = 50
    safety_class: Literal[2] = 2
    environment_class: Literal['I'] = 'I'
    crack_limit_mm: float = Field(gt=0, le=0.3)
    deflection_limit_ratio: float = Field(ge=200)
    end_anchor_length_mm: float = Field(gt=0)
    end_anchor_stirrup_spacing_mm: float = Field(gt=0)
    top_bar_diameter_mm: float = Field(ge=10)
    top_bar_count: int = Field(ge=2, strict=True)
    side_bar_diameter_mm: float = Field(default=0, ge=0)
    side_bar_count_per_face: int = Field(default=0, ge=0, strict=True)
    side_bar_spacing_mm: float | None = Field(default=None, gt=0)
    support_width_mm: float = Field(gt=0)
    shear_position_mm: float | None = Field(default=None, ge=0)

    @field_validator('bar_diameter_mm', 'stirrup_diameter_mm', 'top_bar_diameter_mm', 'side_bar_diameter_mm')
    @classmethod
    def supported_diameter(cls, value, info):
        return validate_diameter(info.field_name, value)

    @model_validator(mode='before')
    @classmethod
    def no_bools(cls, values):
        if any(isinstance(v, bool) for v in values.values()):
            raise ValueError('布尔值不能代替工程数值')
        return values


CN_UNITS = {name: ('kN·m' if name.endswith('_kn_m') and name == 'design_moment_kn_m'
                   else 'kN' if name.endswith('_kn') else 'mm' if name.endswith('_mm')
                   else 'kN/m' if name.endswith('_kn_m') else 'kN/m3' if name.endswith('_kn_m3')
                   else None) for name in CNParameters.model_fields}
CN_INTEGERS = {'reinforcement_layers', 'bar_count', 'stirrup_legs', 'design_life_years',
               'safety_class', 'top_bar_count', 'side_bar_count_per_face'}


def cn_required(request):
    # Partial flexure can operate directly on a confirmed design moment without loads/SLS.
    basic = {'support_type', 'load_case', 'section_type', 'reinforcement_layers', 'span_mm',
             'concrete_grade', 'steel_grade', 'cover_mm', 'bar_diameter_mm', 'stirrup_diameter_mm',
             'importance_factor',
             'design_life_years', 'safety_class', 'environment_class'}
    if request.task_type == 'evaluate_existing':
        basic |= {'beam_width_mm', 'beam_depth_mm', 'bar_count'}
    targets = set(request.targets)
    if 'design_moment_kn_m' not in request.parameters or targets - {'flexure'} or request.task_type == 'new_design':
        basic |= {'dead_load_kn_m', 'live_load_kn_m', 'live_quasi_factor',
                  'live_combination_factor', 'live_frequency_factor', 'self_weight_mode'}
        if request.parameters.get('self_weight_mode') and request.parameters['self_weight_mode'].value=='excluded':
            basic.add('concrete_unit_weight_kn_m3')
    if request.task_type == 'new_design' or 'shear' in targets:
        basic |= {'stirrup_grade', 'stirrup_legs', 'support_width_mm'}
        if request.task_type == 'evaluate_existing':
            basic.add('stirrup_spacing_mm')
    if 'detailing' in targets or request.task_type == 'new_design':
        basic |= {'aggregate_size_mm', 'end_anchor_length_mm', 'end_anchor_stirrup_spacing_mm', 'top_bar_diameter_mm', 'top_bar_count',
                  'side_bar_diameter_mm', 'side_bar_count_per_face', 'support_width_mm'}
    if 'crack' in targets:
        basic.add('crack_limit_mm')
    if 'deflection' in targets:
        basic.add('deflection_limit_ratio')
    return basic


class ParameterValue(Contract):
    value: float | str | bool
    unit: str | None = None
    source: Literal["user", "llm_extracted", "tool", "derived", "default_confirmed", "template"] = "user"
    confirmed: bool = False
    raw_value: float | str | bool | None = None
    raw_unit: str | None = None
    revision: int = 1


Target = Literal["flexure", "shear", "detailing", "crack", "deflection"]


class TaskRequest(Contract):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, validate_assignment=True)
    code: Literal["cn-2024"] = "cn-2024"
    auto_redesign: bool = False
    max_iterations: int = Field(default=12, ge=1, le=40)
    task_type: Literal["new_design", "evaluate_existing", "unsupported"]
    parameters: dict[str, ParameterValue] = Field(default_factory=dict)
    targets: list[Target] = Field(default_factory=lambda: ["flexure", "shear", "detailing", "crack", "deflection"])
    search_diameters_mm: list[int] = Field(default_factory=list, max_length=8)
    solution_count: int = Field(default=1, ge=1, le=3)
    user_query: str = ""
    clarification: list[str] = Field(default_factory=list)

    @model_validator(mode='before')
    @classmethod
    def design_defaults(cls, value):
        if isinstance(value, dict) and value.get('task_type') == 'new_design' and 'auto_redesign' not in value:
            return {**value, 'auto_redesign': True}
        return value

    @field_validator('search_diameters_mm')
    @classmethod
    def search_catalog(cls, value):
        if len(value) != len(set(value)):
            raise ValueError('候选直径不能重复')
        for diameter in value:
            validate_diameter('bar_diameter_mm', diameter)
        return value

    @field_validator("targets")
    @classmethod
    def targets_not_empty(cls, value):
        if not value or len(value) != len(set(value)):
            raise ValueError("验算目标不能为空或重复")
        return value


# Supported input units are normalized before CN parameter validation.
FACTORS = {
    "mm": {"mm": 1, "m": 1000, "cm": 10},
    "kN/m": {"kN/m": 1, "N/mm": 1, "N/m": 0.001},
    "kN/m3": {"kN/m3": 1, "N/m3": 0.001},
}


def parameter_python(name: str, item: ParameterValue):
    return int(item.value) if name in {"bar_count", "stirrup_legs", "reinforcement_layers", "design_life_years", "safety_class", "top_bar_count", "side_bar_count_per_face"} else item.value


class ToolResult(Contract):
    tool: str
    status: Literal["success", "failed", "blocked"]
    inputs_hash: str
    inputs: dict[str, Any]
    outputs: dict[str, Any] = Field(default_factory=dict)
    code_refs: list[str] = Field(default_factory=lambda: ["docs/rc_beam_cn_design_spec.md"])
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    calculation_steps: list[dict[str, Any]] = Field(default_factory=list)
    revision: int = 1
    formula_version: str = "cn-rc-2024-v1"


class EvaluationResult(Contract):
    status: Literal["pass", "fail", "incomplete", "error"] = "incomplete"
    checks: dict[str, bool] = Field(default_factory=dict)
    code_status: Literal["未完成", "已核验支持范围内项目"] = "未完成"
    overall_status: Literal["incomplete", "pass", "fail", "error"] = "incomplete"
    unimplemented: list[str] = Field(default_factory=lambda: ["尚未完成请求项目验算", "节点详图、施工与完整工程审查"])


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
    profile: CNProfile = Field(default_factory=CNProfile)
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
    cache: dict[str, ToolResult] = Field(default_factory=dict)
    plan_trace: list[dict[str, Any]] = Field(default_factory=list)
    revisions: list[dict[str, Any]] = Field(default_factory=list)
    revision_reason: str = '初始任务'
    design_alternatives: list[dict[str, Any]] = Field(default_factory=list)
    search_stop_reason: str = ''
    design_search: dict[str, Any] = Field(default_factory=dict)
