"""Rebuild transparent integer-valued examples (no network and no secrets)."""
import json
from pathlib import Path

base = dict(support_type='simply_supported',load_case='full_span_udl',section_type='rectangular',
    reinforcement_layers=1,span_mm=6000,concrete_grade='C30',steel_grade='HRB400',stirrup_grade='HRB400',
    beam_width_mm=300,beam_depth_mm=550,cover_mm=30,bar_diameter_mm=20,stirrup_diameter_mm=8,
    stirrup_legs=2,aggregate_size_mm=20,dead_load_kn_m=10,live_load_kn_m=5,self_weight_mode='excluded',
    concrete_unit_weight_kn_m3=25,live_quasi_factor=.5,live_combination_factor=.7,live_frequency_factor=.6,
    importance_factor=1,design_life_years=50,safety_class=2,environment_class='I',crack_limit_mm=.3,
    deflection_limit_ratio=250,end_anchor_length_mm=800,end_anchor_stirrup_spacing_mm=100,
    top_bar_diameter_mm=12,top_bar_count=2,side_bar_diameter_mm=12,side_bar_count_per_face=2,
    side_bar_spacing_mm=180,support_width_mm=1000)

def fixture(name,values,task='new_design',targets=None,auto=False):
    from engi_agent.engineering.cn_schema import CN_UNITS
    document={'code':'cn-2024','task_type':task,'auto_redesign':auto,'max_iterations':3,
              'targets':targets or ['flexure','shear','detailing','crack','deflection'],
              'parameters':{k:{'value':v,'unit':CN_UNITS[k],'source':'user'} for k,v in values.items()}}
    path=Path('examples/engineering')/(name+'.json')
    path.write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    fixture('cn_design',base)
    fixture('cn_existing',{**base,'bar_count':3,'stirrup_spacing_mm':250},'evaluate_existing')
    partial={k:v for k,v in base.items() if k in {'support_type','load_case','section_type','reinforcement_layers',
             'span_mm','concrete_grade','steel_grade','cover_mm','bar_diameter_mm','stirrup_diameter_mm',
             'self_weight_mode','concrete_unit_weight_kn_m3','importance_factor','design_life_years','safety_class',
             'environment_class','beam_width_mm','beam_depth_mm'}}
    fixture('cn_flexure_only',{**partial,'bar_count':3,'design_moment_kn_m':100},'evaluate_existing',['flexure'])
    fixture('cn_redesign',{**base,'deflection_limit_ratio':600},auto=True)
    fixture('cn_no_solution',{**base,'crack_limit_mm':.01},auto=True)
