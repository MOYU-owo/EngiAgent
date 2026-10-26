"""Input boundary for the deliberately small Chinese-code beam implementation."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)


class CNProfile(Contract):
    version: Literal['cn-rc-2024-v1'] = 'cn-rc-2024-v1'
    source: str = 'GB/T 50010-2010（2024修订+2015未修订条文）；GB 55001-2021；GB 55008-2021；GB 50009-2012'
    gamma_dead: Literal[1.3] = 1.3
    gamma_live: Literal[1.5] = 1.5
    source_note: str = '普通房屋、50年、二级安全、单一不利重力可变作用；不含抗震专项'


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
