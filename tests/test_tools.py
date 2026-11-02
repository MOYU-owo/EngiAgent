"""CN tool registry and numerical contracts reject invalid verdicts and values."""
import pytest
from engi_agent.engineering.cn_tools import REGISTRY
from engi_agent.engineering.cn_outputs import validate_output
from engi_agent.engineering.errors import EngineeringFailure
from engi_agent.engineering.dependency_graph import SPECS


def test_cn_registry_has_exactly_the_declared_dag_tools():
    assert set(REGISTRY) == set(SPECS)
    assert "materials" in REGISTRY and "crack_check" in REGISTRY and "deflection_check" in REGISTRY
    assert "elastic_deflection" not in REGISTRY and "calculator" not in REGISTRY


@pytest.mark.parametrize("grade,fc,fy", [("C30",14.3,360),("C40",19.1,360),("C50",23.1,360)])
def test_materials_are_cn_design_strengths(grade,fc,fy):
    result = REGISTRY["materials"]({"concrete_grade":grade,"steel_grade":"HRB400","stirrup_grade":"HRB400"},{})
    assert result["fc_mpa"] == fc and result["fy_mpa"] == fy
    assert validate_output("materials",result) == result


def test_material_code_restriction_is_engineering_failure():
    with pytest.raises(EngineeringFailure):
        REGISTRY["materials"]({"concrete_grade":"C25","steel_grade":"HRB500"},{})


@pytest.mark.parametrize("changes", [
    {"crack_width_mm":float("nan")}, {"crack_width_mm":float("inf")},
    {"crack_width_mm":-.1}, {"limit_mm":0}, {"pass":"true"},
    {"pass":True,"reasons":["不通过"]}, {"pass":False,"reasons":[]},
])
def test_invalid_numerical_outputs_and_inconsistent_verdicts_rejected(changes):
    valid = {"crack_width_mm":.1,"limit_mm":.3,"sigma_s_mpa":100.,"psi":.5,"rho_te":.01,"pass":True,"reasons":[]}
    with pytest.raises(ValueError): validate_output("crack_check", {**valid,**changes})


def test_missing_required_cn_outputs_cannot_be_a_pass():
    with pytest.raises(ValueError): validate_output("flexural_check", {"pass":True,"reasons":[]})
