"""Small explicit engineering DAG. Functions, dependencies and inputs are whitelisted."""
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ToolSpec:
    fields: tuple[str, ...]
    dependencies: tuple[str, ...] = ()
    version: str = 'cn-rc-2024-v1'


SPECS = {
    'materials': ToolSpec(('concrete_grade', 'steel_grade', 'stirrup_grade')),
    'section_sizing': ToolSpec(('span_mm', 'beam_width_mm', 'beam_depth_mm', 'max_width_mm', 'max_depth_mm')),
    'section_geometry': ToolSpec(('span_mm', 'cover_mm', 'bar_diameter_mm', 'stirrup_diameter_mm'), ('section_sizing',)),
    'load_combination': ToolSpec(('dead_load_kn_m', 'live_load_kn_m', 'self_weight_mode',
                                 'concrete_unit_weight_kn_m3', 'live_quasi_factor',
                                 'live_combination_factor', 'live_frequency_factor')),
    'beam_analysis': ToolSpec(('span_mm', 'support_width_mm', 'shear_position_mm'), ('load_combination',)),
    'demand': ToolSpec(('design_moment_kn_m', 'design_shear_kn')),
    'flexural_design': ToolSpec(('bar_diameter_mm', 'minimum_bar_count'), ('section_geometry', 'materials', 'demand')),
    'shear_design': ToolSpec(('stirrup_legs', 'stirrup_diameter_mm'), ('section_geometry', 'materials', 'demand')),
    'flexural_check': ToolSpec(('bar_count',), ('section_geometry', 'materials', 'demand')),
    'shear_check': ToolSpec(('stirrup_legs', 'stirrup_spacing_mm'), ('section_geometry', 'materials', 'demand')),
    'detailing_check': ToolSpec(('span_mm', 'concrete_grade', 'bar_count', 'aggregate_size_mm', 'cover_mm', 'bar_diameter_mm',
                                 'stirrup_diameter_mm', 'stirrup_spacing_mm', 'end_anchor_length_mm',
                                 'end_anchor_stirrup_spacing_mm', 'top_bar_count', 'top_bar_diameter_mm', 'side_bar_diameter_mm',
                                 'side_bar_count_per_face', 'side_bar_spacing_mm', 'support_width_mm'),
                                ('section_geometry', 'materials')),
    'crack_check': ToolSpec(('bar_count', 'bar_diameter_mm', 'cover_mm', 'stirrup_diameter_mm', 'crack_limit_mm'),
                           ('section_geometry', 'materials', 'beam_analysis')),
    'deflection_check': ToolSpec(('bar_count', 'cover_mm', 'bar_diameter_mm', 'stirrup_diameter_mm', 'span_mm',
                                 'deflection_limit_ratio'), ('section_geometry', 'materials', 'beam_analysis')),
}
TARGET_TOOLS = {'flexure': 'flexural_check', 'shear': 'shear_check', 'detailing': 'detailing_check',
                'crack': 'crack_check', 'deflection': 'deflection_check'}


def dependencies(name, parameters, targets):
    result = list(SPECS[name].dependencies)
    if name == 'load_combination' and parameters.get('self_weight_mode') == 'excluded':
        result.append('section_sizing')
    if name == 'demand':
        if ('flexure' in targets and parameters.get('design_moment_kn_m') is None
                or 'shear' in targets and parameters.get('design_shear_kn') is None):
            result.append('beam_analysis')
    return tuple(result)


def build_plan(targets, parameters, *, design=False):
    """Dependency closure + stable topological order; a cycle is a programming error."""
    roots = ['flexural_design', 'shear_design'] if design else [TARGET_TOOLS[t] for t in targets]
    ordered, visiting = [], set()
    def visit(name):
        if name in visiting:
            raise ValueError('工程依赖图存在环')
        if name in ordered:
            return
        visiting.add(name)
        for dependency in dependencies(name, parameters, targets):
            visit(dependency)
        visiting.remove(name)
        ordered.append(name)
    for root in roots:
        visit(root)
    return ordered
