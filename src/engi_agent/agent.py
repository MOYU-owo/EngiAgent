"""The complete, intentionally small LangGraph ReAct loop."""

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from langchain.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from engi_agent.config import Settings
from engi_agent.prompts.system_prompt import SYSTEM_PROMPT
from engi_agent.tools import TOOLS


@dataclass(frozen=True)
class AgentResponse:
    content: str
    tool_events: list[str] = field(default_factory=list)


def create_deepseek_model(settings: Settings) -> ChatDeepSeek:
    """Create the tool-capable DeepSeek chat model."""
    return ChatDeepSeek(
        model=settings.model,
        api_key=settings.deepseek_api_key,
        temperature=settings.temperature,
        max_retries=settings.max_retries,
    )


def build_graph(
    model: Any | None = None,
    checkpointer: Any | None = None,
):
    """Build START -> agent -> tools -> agent -> END.

    A model can be injected so the graph is testable without a network or API key.
    """
    if model is None:
        model = create_deepseek_model(Settings.from_env())

    # Tool registration exposes the schemas so the LLM can choose an action.
    model_with_tools = model.bind_tools(TOOLS)

    def call_model(state: MessagesState) -> dict[str, list[AIMessage]]:
        response = model_with_tools.invoke(
            [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        )
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", call_model)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "agent")

    # If the AIMessage has tool_calls, go to ToolNode; otherwise finish.
    builder.add_conditional_edges("agent", tools_condition, ["tools", END])
    builder.add_edge("tools", "agent")

    # The in-memory checkpointer keeps messages for each thread_id.
    return builder.compile(checkpointer=checkpointer or InMemorySaver())


class EngiAgent:
    """Small application wrapper around the compiled graph."""

    def __init__(self, graph: Any | None = None, thread_id: str | None = None):
        self.graph = graph or build_graph()
        self.thread_id = thread_id or str(uuid4())

    def run_turn(self, user_input: str) -> AgentResponse:
        if not user_input.strip():
            raise ValueError("User input cannot be empty.")

        config = {"configurable": {"thread_id": self.thread_id}}
        result = self.graph.invoke(
            {"messages": [HumanMessage(content=user_input)]}, config=config
        )
        turn_messages = _messages_after_last_human(result["messages"])
        final_message = next(
            (
                message
                for message in reversed(turn_messages)
                if isinstance(message, AIMessage) and not message.tool_calls
            ),
            None,
        )
        if final_message is None:
            raise RuntimeError("Agent did not produce a final answer.")

        return AgentResponse(
            content=str(final_message.content),
            tool_events=_format_tool_events(turn_messages),
        )


def _messages_after_last_human(messages: list[Any]) -> list[Any]:
    for index in range(len(messages) - 1, -1, -1):
        if isinstance(messages[index], HumanMessage):
            return messages[index + 1 :]
    return messages


def _format_tool_events(messages: list[Any]) -> list[str]:
    events: list[str] = []
    for message in messages:
        if isinstance(message, AIMessage):
            for call in message.tool_calls:
                events.append(f"[Tool call] {call['name']}({call['args']})")
        elif isinstance(message, ToolMessage):
            events.append(f"[Tool result] {message.name}: {message.content}")
    return events
