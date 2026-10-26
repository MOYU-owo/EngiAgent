"""Minimum required numerical output contracts, validated before cache or verdict."""
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, create_model


class Output(BaseModel):
    model_config=ConfigDict(extra='allow',allow_inf_nan=False)


POS=(float,Field(gt=0))
NONNEG=(float,Field(ge=0))
CHECK={'pass':(StrictBool,...),'reasons':(list[str],...)}
GEOMETRY={'beam_width_mm':POS,'beam_depth_mm':POS,'effective_depth_mm':POS,'bar_area_mm2':POS,'stirrup_area_mm2':POS,'gross_inertia_mm4':POS}
FLEX={'As_mm2':POS,'bar_count':(StrictInt,Field(ge=2)),'capacity_kn_m':NONNEG,
      'demand_kn_m':NONNEG,'compression_zone_mm':NONNEG,'minimum_steel_mm2':POS,**CHECK}
CONTRACTS={
    'materials':{'fc_mpa':POS,'ft_mpa':POS,'ftk_mpa':POS,'fy_mpa':POS,'Es_mpa':POS,'Ec_mpa':POS,'xi_b':POS},
    'section_sizing':{'beam_width_mm':POS,'beam_depth_mm':POS,'sizing_basis':(str,...)},
    'section_geometry':GEOMETRY,
    'load_combination':{k:NONNEG for k in ('total_dead_load_kn_m','added_self_weight_kn_m','ultimate_load_kn_m','standard_load_kn_m','quasi_load_kn_m')},
    'beam_analysis':{**{k:NONNEG for k in ('Mu_kn_m','Vu_max_kn','standard_moment_kn_m','quasi_moment_kn_m','quasi_load_kn_m')},'Vu_design_kn':(float|None,...)},
    'demand':{'Mu_kn_m':(float|None,...),'Vu_design_kn':(float|None,...),'moment_source':(str,...),'shear_source':(str,...)},
    'flexural_design':{**FLEX,'required_steel_mm2':NONNEG,'bar_diameter_mm':POS},
    'flexural_check':FLEX,
    'shear_design':{'stirrup_spacing_mm':POS,'required_av_over_s':NONNEG,'maximum_spacing_mm':POS,'demand_kn':NONNEG},
    'shear_check':{'capacity_kn':NONNEG,'demand_kn':NONNEG,'section_limit_kn':POS,**CHECK},
    'detailing_check':{'clear_spacing_mm':(float,...),'required_anchor_mm':POS,'provided_anchor_mm':POS,**CHECK},
    'crack_check':{'crack_width_mm':NONNEG,'limit_mm':POS,'sigma_s_mpa':NONNEG,'psi':POS,'rho_te':POS,**CHECK},
    'deflection_check':{'deflection_mm':NONNEG,'limit_mm':POS,'long_term_stiffness_n_mm2':POS,'short_term_stiffness_n_mm2':POS,**CHECK},
}
MODELS={k:create_model(k+'_output',__base__=Output,**fields) for k,fields in CONTRACTS.items()}


def validate_output(name,outputs):
    result=MODELS[name].model_validate(outputs).model_dump()
    if 'pass' in result and result['pass'] != (not result['reasons']):
        raise ValueError('工具判定与失败原因不一致')
    return result
