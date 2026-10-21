"""Per-tool output contracts: reject missing, non-finite and wrongly typed results."""
from pydantic import BaseModel, ConfigDict, Field


class Output(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Sizing(Output):
    beam_width_mm: float
    beam_depth_mm: float
    sizing_basis: str


class Geometry(Output):
    beam_width_mm: float
    beam_depth_mm: float
    effective_depth_mm: float
    gross_inertia_mm4: float
    bar_area_mm2: float
    stirrup_area_mm2: float


class Loads(Output):
    self_weight_kn_m: float | None
    self_weight_mode: str
    total_dead_load_kn_m: float
    strength_combinations_kn_m: dict[str, float]
    governing_combination: str
    ultimate_load_kn_m: float
    service_load_kn_m: float


class Analysis(Output):
    Mu_kn_m: float
    Vu_max_kn: float
    reaction_left_kn: float
    reaction_right_kn: float
    shear_position_mm: float
    Vu_at_position_kn: float
    critical_shear_position_mm: float
    Vu_design_kn: float
    service_moment_kn_m: float
    service_shear_kn: float


class Layout(Output):
    center_spacing_mm: float
    clear_spacing_mm: float
    minimum_clear_spacing_mm: float
    maximum_center_spacing_mm: float
    # JSON property is named pass; Python reserves that word.
    passed: bool = Field(alias="pass")
    reasons: list[str]


class Capacity(Output):
    As_mm2: float
    compression_block_mm: float
    neutral_axis_mm: float
    beta1: float
    tension_strain: float
    tension_controlled: bool
    capacity_kn_m: float
    minimum_steel_mm2: float


class FlexuralDesign(Capacity):
    required_steel_mm2: float
    bar_count: int
    bar_diameter_mm: float
    layout: Layout


class FlexuralCheck(Capacity):
    demand_kn_m: float
    passed: bool = Field(alias="pass")
    reasons: list[str]


class ShearTerms(Output):
    concrete_capacity_n: float
    required_stirrup_strength_n: float
    maximum_stirrup_strength_n: float
    minimum_av_over_s: float
    maximum_spacing_mm: float
    Av_mm2: float
    demand_kn: float


class ShearDesign(ShearTerms):
    stirrup_spacing_mm: float
    stirrup_legs: int
    stirrup_diameter_mm: float
    arrangement: str


class ShearCheck(ShearTerms):
    capacity_kn: float
    provided_stirrup_strength_n: float
    passed: bool = Field(alias="pass")
    reasons: list[str]


class Deflection(Output):
    deflection_mm: float
    limit_mm: float
    gross_inertia_mm4: float
    service_load_kn_m: float
    passed: bool = Field(alias="pass")
    reasons: list[str]
    model: str


OUTPUT_MODELS = {
    "section_sizing": Sizing, "section_geometry": Geometry, "load_combination": Loads,
    "beam_analysis": Analysis, "flexural_design": FlexuralDesign, "shear_design": ShearDesign,
    "flexural_check": FlexuralCheck, "detailing_check": Layout, "shear_check": ShearCheck,
    "elastic_deflection": Deflection,
}
