from langchain.messages import AIMessage

from engi_agent.agent import EngiAgent, build_graph


class ScriptedModel:
    """Small fake chat model that returns a predetermined response sequence."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.bound_tools = None
        self.invocations = []

    def bind_tools(self, tools):
        self.bound_tools = tools
        return self

    def invoke(self, messages):
        self.invocations.append(messages)
        return self.responses.pop(0)


def make_agent(responses, thread_id="test-thread"):
    model = ScriptedModel(responses)
    return EngiAgent(build_graph(model=model), thread_id=thread_id), model


def test_case_1_normal_chat_does_not_call_tools():
    agent, _ = make_agent([AIMessage(content="你好！")])
    response = agent.run_turn("你好")
    assert response.content == "你好！"
    assert response.tool_events == []


def test_case_2_calculation_calls_calculator():
    agent, _ = make_agent(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "calculator",
                        "args": {"expression": "12.5 * 8"},
                        "id": "calc-1",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(content="结果是 100。"),
        ]
    )
    response = agent.run_turn("计算 12.5 × 8。")
    assert response.content == "结果是 100。"
    assert any("calculator" in event for event in response.tool_events)
    assert any("100.0" in event for event in response.tool_events)


def test_case_3_knowledge_question_calls_knowledge_tool():
    agent, _ = make_agent(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_demo_knowledge",
                        "args": {"query": "安全系数"},
                        "id": "knowledge-1",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(content="Demo 安全系数是 1.5。"),
        ]
    )
    response = agent.run_turn("demo 规范中的安全系数是多少？")
    assert "1.5" in response.content
    assert any("get_demo_knowledge" in event for event in response.tool_events)


def test_case_4_combined_question_calls_both_tools():
    agent, _ = make_agent(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "calculator",
                        "args": {"expression": "12.5 * 8"},
                        "id": "calc-2",
                        "type": "tool_call",
                    },
                    {
                        "name": "get_demo_knowledge",
                        "args": {"query": "安全系数"},
                        "id": "knowledge-2",
                        "type": "tool_call",
                    },
                ],
            ),
            AIMessage(content="计算结果为 100，Demo 安全系数为 1.5。"),
        ]
    )
    response = agent.run_turn("计算 12.5 × 8，同时告诉我安全系数。")
    calls = [event for event in response.tool_events if event.startswith("[Tool call]")]
    assert len(calls) == 2
    assert any("calculator" in event for event in calls)
    assert any("get_demo_knowledge" in event for event in calls)


def test_case_5_checkpointer_keeps_multi_turn_messages():
    agent, model = make_agent(
        [
            AIMessage(content="好的，我记住当前项目跨度是 6m。"),
            AIMessage(content="刚才的跨度是 6m。"),
        ],
        thread_id="memory-case",
    )
    agent.run_turn("记住当前项目跨度是 6m。")
    response = agent.run_turn("刚才的跨度是多少？")

    second_call_text = " ".join(str(message.content) for message in model.invocations[1])
    assert "当前项目跨度是 6m" in second_call_text
    assert response.content == "刚才的跨度是 6m。"
