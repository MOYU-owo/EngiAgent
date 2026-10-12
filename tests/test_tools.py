import pytest

from engi_agent.tools.calculator import CalculatorError, calculator, evaluate_expression
from engi_agent.tools.knowledge import get_demo_knowledge, search_demo_knowledge


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("12.5 * 8", 100.0),
        ("12.5 × 8", 100.0),
        ("(2 + 3) ** 2", 25),
        ("7 // 2", 3),
    ],
)
def test_evaluate_expression(expression, expected):
    assert evaluate_expression(expression) == expected


@pytest.mark.parametrize(
    "expression",
    ["__import__('os').getcwd()", "open('secret')", "2 ** 1000", "True + 1"],
)
def test_calculator_rejects_unsafe_or_unbounded_input(expression):
    with pytest.raises(CalculatorError):
        evaluate_expression(expression)


def test_calculator_tool():
    assert calculator.invoke({"expression": "12.5 * 8"}) == "100.0"


def test_demo_knowledge_finds_safety_factor():
    result = search_demo_knowledge("demo 规范中的安全系数是多少？")
    assert "1.5" in result
    assert "knowledge/demo_knowledge.md" in result


def test_demo_knowledge_tool():
    result = get_demo_knowledge.invoke({"query": "默认单位是什么？"})
    assert "SI" in result


def test_demo_knowledge_reports_no_match():
    assert "未找到" in search_demo_knowledge("火星土壤颜色")
