"""A small, deterministic arithmetic tool with no use of eval()."""

import ast
import math
import operator

from langchain.tools import tool


class CalculatorError(ValueError):
    """Raised when an expression is unsupported or unsafe."""


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_MAX_EXPRESSION_LENGTH = 200
_MAX_ABS_EXPONENT = 20
_MAX_ABS_RESULT = 1e100


def evaluate_expression(expression: str) -> int | float:
    """Evaluate a restricted arithmetic expression deterministically."""
    normalized = expression.strip().replace("×", "*").replace("÷", "/")
    if not normalized:
        raise CalculatorError("Expression cannot be empty.")
    if len(normalized) > _MAX_EXPRESSION_LENGTH:
        raise CalculatorError("Expression is too long.")

    try:
        tree = ast.parse(normalized, mode="eval")
    except SyntaxError as exc:
        raise CalculatorError("Invalid arithmetic expression.") from exc

    result = _evaluate_node(tree.body)
    if isinstance(result, float) and not math.isfinite(result):
        raise CalculatorError("Result must be finite.")
    if abs(result) > _MAX_ABS_RESULT:
        raise CalculatorError("Result is outside the supported range.")
    return result


def _evaluate_node(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise CalculatorError("Only numeric literals are allowed.")
        return node.value

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate_node(node.operand))

    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > _MAX_ABS_EXPONENT:
            raise CalculatorError("Exponent is outside the supported range.")
        try:
            value = _BINARY_OPERATORS[type(node.op)](left, right)
        except (ArithmeticError, OverflowError) as exc:
            raise CalculatorError(f"Calculation failed: {exc}") from exc
        if isinstance(value, complex):
            raise CalculatorError("Complex results are not supported.")
        if abs(value) > _MAX_ABS_RESULT:
            raise CalculatorError("Intermediate result is outside the supported range.")
        return value

    raise CalculatorError(
        "Unsupported expression. Use only numbers, parentheses, and arithmetic operators."
    )


@tool
def calculator(expression: str) -> str:
    """Calculate a mathematical expression exactly with a deterministic tool.

    Use this for arithmetic instead of calculating mentally. Supported operators
    are +, -, *, /, //, %, **, unary signs, and parentheses.
    """
    return str(evaluate_expression(expression))
