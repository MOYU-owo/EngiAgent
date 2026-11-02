"""Structured CN model roles; no generic chat/tool-execution runtime remains."""
import pytest
from engi_agent.engineering.roles import DeepSeekRoles, RolePlan
from engi_agent.engineering.cn_schema import TaskRequest
from engi_agent.engineering.cn_workflow import prepare


class ScriptedModel:
    def __init__(self, response):
        self.response = response
        self.messages = []
        self.contract = None

    def with_structured_output(self, contract, method):
        self.contract = contract
        assert method == "function_calling"
        return self

    def invoke(self, messages):
        self.messages = messages
        return self.response


def test_unspecified_standard_defaults_to_cn_without_supplying_engineering_defaults():
    model = ScriptedModel({"task_type": "new_design", "parameters": {"span_mm": {"value": 6, "unit": "m"}}})
    parsed = DeepSeekRoles(model).parse("新设计简支梁，跨度6m")
    assert model.contract is TaskRequest and parsed.code == "cn-2024"
    assert parsed.user_query == "新设计简支梁，跨度6m"
    assert set(parsed.parameters) == {"span_mm"}
    assert parsed.parameters["span_mm"].source == "llm_extracted"
    assert not parsed.parameters["span_mm"].confirmed
    assert "concrete_grade" in prepare(parsed).missing_parameters
    prompt = model.messages[0].content
    assert "仅支持中国规范" in prompt and "cn-2024" in prompt
    assert "code=teaching" not in prompt and "phi_flexure" not in prompt


@pytest.mark.parametrize("code", ["teaching", "ACI318-19", "eurocode"])
def test_provider_cannot_select_another_standard(code):
    model = ScriptedModel({"code": code, "task_type": "new_design"})
    with pytest.raises(ValueError): DeepSeekRoles(model).parse("设计一根梁")


@pytest.mark.parametrize("query", ["按ACI 318-19设计简支梁", "采用美标设计梁", "依据Eurocode验算梁", "Use ACI 318 for beam design"])
def test_explicit_foreign_code_request_is_rejected_without_model_calls(query):
    model = ScriptedModel(None)
    result = DeepSeekRoles(model).parse(query)
    assert result.code == "cn-2024" and result.task_type == "unsupported"
    assert result.clarification and not model.messages


def test_model_plan_returns_only_structured_steps_and_explanation():
    model = ScriptedModel({"steps": ["materials", "flexural_check"], "explanation": "先取材料再验算"})
    plan = DeepSeekRoles(model).plan("Evaluation", {"required_steps": ["materials", "flexural_check"]})
    assert model.contract is RolePlan and plan.steps == ["materials", "flexural_check"]
    assert "不计算数值" in model.messages[0].content
