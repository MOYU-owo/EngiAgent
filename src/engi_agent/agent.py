"""EngiAgent 的核心运行逻辑：一个刻意保持精简的 LangGraph ReAct 循环。

可以先把整个文件理解成下面这条流水线：

    用户输入
      -> agent 节点让大模型判断下一步
      -> 如果模型请求 Tool，则进入 tools 节点执行 Tool
      -> Tool 结果回到 agent 节点
      -> 模型生成不再包含 Tool 调用的最终回答

这里的 ``agent`` 和 ``tools`` 是 Graph 中的两个“节点”，不是两个不同的
AI Agent。真正负责理解和组织回答的是 DeepSeek；Tool 负责执行确定性的动作。
"""

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
    """返回给 CLI 的简化结果。

    LangGraph 内部保存的是完整消息列表。CLI 不需要理解所有消息类型，所以
    ``run_turn`` 最后将它们整理成最终文本和便于阅读的 Tool 轨迹。
    """

    content: str
    tool_events: list[str] = field(default_factory=list)


def create_deepseek_model(settings: Settings) -> ChatDeepSeek:
    """根据配置创建 DeepSeek 对话模型。

    这里只创建模型客户端，还没有把 Tool 交给模型。Tool 会在 ``build_graph``
    中通过 ``bind_tools`` 绑定。
    """
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
    """构建并编译 ``START -> agent -> tools -> agent -> END`` 工作流。

    ``model`` 和 ``checkpointer`` 都允许从外部传入。测试时可以注入假模型，
    因而不需要联网或使用真实 API Key；正常运行时则使用 DeepSeek 和内存存档器。
    """
    # 没有传入模型时，才从 .env 读取配置并创建真实 DeepSeek 客户端。
    if model is None:
        model = create_deepseek_model(Settings.from_env())

    # bind_tools 不会立即执行 Python 函数。
    # 它只是把每个 Tool 的名称、说明和参数格式告诉模型，使模型可以返回类似：
    # {"name": "calculator", "args": {"expression": "12.5 * 8"}}
    # 的结构化调用请求。真正执行函数的是后面的 ToolNode。
    model_with_tools = model.bind_tools(TOOLS)

    def call_model(state: MessagesState) -> dict[str, list[AIMessage]]:
        """Graph 的 agent 节点：读取历史消息，并追加一条模型消息。

        ``state["messages"]`` 里可能包含用户消息、以前的模型消息和 Tool
        返回结果。每次调用都把 SYSTEM_PROMPT 放在最前面，再交给模型判断：
        是直接回答，还是请求调用一个或多个 Tool。
        """
        response = model_with_tools.invoke(
            [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        )

        # 节点只返回本次新增的消息。MessagesState 会负责把它追加到原消息列表，
        # 因此这里不需要手动复制全部历史。
        return {"messages": [response]}

    # MessagesState 是 Graph 的共享状态，目前核心字段是 messages。
    builder = StateGraph(MessagesState)

    # agent 节点负责让模型“思考下一步”；tools 节点负责执行模型请求的 Tool。
    builder.add_node("agent", call_model)
    builder.add_node("tools", ToolNode(TOOLS))

    # 每次 Graph 调用都从 agent 节点开始，因此普通聊天也会先交给模型判断。
    builder.add_edge(START, "agent")

    # tools_condition 检查 agent 最新返回的 AIMessage：
    # - 有 tool_calls：进入 tools 节点；
    # - 没有 tool_calls：说明这已经是最终回答，进入 END。
    builder.add_conditional_edges("agent", tools_condition, ["tools", END])

    # ToolNode 会把执行结果写成 ToolMessage。结果必须回到 agent 节点，
    # 让模型读取 Tool 的真实输出，再决定继续调用 Tool 还是形成最终回答。
    builder.add_edge("tools", "agent")

    # compile 将“节点 + 边”变成可运行的 Graph。
    # InMemorySaver 按 thread_id 保存消息，使同一进程中的多轮对话有短期记忆。
    return builder.compile(checkpointer=checkpointer or InMemorySaver())


class EngiAgent:
    """对已编译 Graph 的轻量封装，供 CLI 和示例代码直接调用。"""

    def __init__(self, graph: Any | None = None, thread_id: str | None = None):
        # 测试可以传入自己的 Graph；正常运行则在这里构建真实 Graph。
        self.graph = graph or build_graph()

        # thread_id 相当于会话编号。同一个编号会恢复同一份短期消息历史；
        # 不传时自动生成新编号，也就是开启一段新会话。
        self.thread_id = thread_id or str(uuid4())

    def run_turn(self, user_input: str) -> AgentResponse:
        """运行一轮对话，并返回最终回答及本轮 Tool 轨迹。"""
        if not user_input.strip():
            raise ValueError("User input cannot be empty.")

        # checkpointer 通过 configurable.thread_id 判断应读取哪段会话历史。
        config = {"configurable": {"thread_id": self.thread_id}}

        # graph.invoke 会一直沿着 Graph 的边运行，直到到达 END。
        # 传入的是本轮新增的 HumanMessage；旧消息由 checkpointer 自动恢复。
        result = self.graph.invoke(
            {"messages": [HumanMessage(content=user_input)]}, config=config
        )

        # result["messages"] 包含整段会话。这里只保留最后一条用户消息之后的
        # 内容，避免把以前轮次的 Tool 轨迹重复打印到 CLI。
        turn_messages = _messages_after_last_human(result["messages"])

        # 一轮中可能有多条 AIMessage：前面的消息可能只是 Tool 调用请求。
        # 从后向前寻找第一条“不含 tool_calls”的 AIMessage，才是最终回答。
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

        # 对外只暴露易用的字符串结果，不要求 CLI 理解 LangChain 消息对象。
        return AgentResponse(
            content=str(final_message.content),
            tool_events=_format_tool_events(turn_messages),
        )


def _messages_after_last_human(messages: list[Any]) -> list[Any]:
    """取得最后一条 HumanMessage 之后的消息，也就是当前轮产生的消息。"""
    for index in range(len(messages) - 1, -1, -1):
        if isinstance(messages[index], HumanMessage):
            return messages[index + 1 :]
    return messages


def _format_tool_events(messages: list[Any]) -> list[str]:
    """把 AIMessage/ToolMessage 转换成适合在 CLI 中展示的调用轨迹。"""
    events: list[str] = []
    for message in messages:
        if isinstance(message, AIMessage):
            # AIMessage 中的 tool_calls 表示“模型请求执行 Tool”。
            for call in message.tool_calls:
                events.append(f"[Tool call] {call['name']}({call['args']})")
        elif isinstance(message, ToolMessage):
            # ToolMessage 表示“Tool 已执行完毕，这是返回给模型的结果”。
            events.append(f"[Tool result] {message.name}: {message.content}")
    return events
