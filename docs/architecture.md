# EngiAgent 架构说明

## 0. 如何阅读这份文档

这份文档的目标不是记住 LangGraph 的 API，而是回答一个更基础的问题：**一条用户输入，怎样穿过模型、工具和状态，最终变成一条可信的回答？**

阅读时可以始终抓住下面这条主线：

```text
用户提出问题
    ↓
LLM 判断下一步
    ↓
如果需要外部能力，生成 tool_call
    ↓
Python Tool 执行动作并返回 ToolMessage
    ↓
LLM 读取结果，再次判断或形成最终回答
```

当前 EngiAgent 是一个 **Generic ReAct Agent MVP**。它证明了自然语言、工具调用、循环控制和短期记忆可以形成完整闭环，但它还不是结构设计、岩土设计或结构健康监测系统。理解这个“小闭环”，比提前堆叠工程模块更重要。

本文讨论的事实以当前源码为准，主要入口是 `run.py` 和 `src/engi_agent/agent.py`。

## 1. EngiAgent 当前解决什么问题

### 1.1 为什么不直接调用一次 LLM

如果应用只做闲聊，一次模型调用通常已经足够：输入文本，得到文本。但是工程任务经常同时包含三类工作：

1. 理解用户真正想做什么；
2. 执行必须正确、可重复的动作；
3. 把动作结果解释给用户。

LLM 擅长第一类和第三类工作，却不应被默认当成计算器、数据库或数值分析器。让模型直接“心算” `12.5 × 8`，可能在简单例子上成功，但这种成功不能建立可验证的工程计算边界。让模型凭记忆回答某条规范，也无法证明信息来自哪里、是否是当前版本。

因此，EngiAgent 把任务分成两个角色：

- LLM 负责理解、决策、Tool 选择和语言解释；
- Tool 负责确定性计算或读取明确的数据源。

这并不意味着 Tool 比 LLM 更“智能”。它意味着系统将不同类型的责任交给更合适的执行者。

### 1.2 当前 MVP 建立了什么

当前版本只建立四项基础能力：

- 一个能够决定是否调用工具的 `deepseek-chat` 模型；
- 一个 `Agent → Tool → Agent` 的 LangGraph 循环；
- `calculator` 与 `get_demo_knowledge` 两个示范 Tool；
- 基于 `InMemorySaver` 和 `thread_id` 的短期会话记忆。

这里没有真实规范库或工程求解器。`demo_knowledge.md` 中的安全系数仅用于验证知识 Tool 的路径，不是工程结论。

## 2. 一次用户请求经历了什么

考虑下面的请求：

> 计算 12.5 × 8，并告诉我 demo 规范中的安全系数。

它包含两个不同性质的子任务：数学计算和本地知识查询。完整数据流如下：

```text
run.py
  │ 读取用户字符串
  ▼
EngiAgent.run_turn(user_input)
  │ HumanMessage + thread_id
  ▼
compiled StateGraph
  │
  ├── START
  │     ↓
  ├── agent node: ChatDeepSeek(messages + tool schemas)
  │     ↓
  │   AIMessage(tool_calls=[calculator, get_demo_knowledge])
  │     ↓ conditional edge
  ├── tools node: ToolNode
  │     ├── calculator("12.5 * 8") → "100.0"
  │     └── get_demo_knowledge("安全系数") → 本地 Markdown 片段
  │     ↓
  │   ToolMessage + ToolMessage
  │     ↓ fixed edge
  ├── agent node: ChatDeepSeek(原消息 + ToolMessage)
  │     ↓
  │   AIMessage(final answer, no tool_calls)
  │     ↓ conditional edge
  └── END
        ↓
AgentResponse(content, tool_events)
        ↓
CLI 打印 Tool trace 和最终回答
```

### 2.1 CLI 并不负责“推理”

`run.py` 只做交互层工作：循环读取输入、识别 `exit`/`quit`、调用 `agent.run_turn()`，再打印工具轨迹和答案。CLI 不判断问题是否需要 Tool，也不执行数学表达式。

### 2.2 `run_turn` 把文本变成图输入

当前实现的关键入口是：

```python
config = {"configurable": {"thread_id": self.thread_id}}
result = self.graph.invoke(
    {"messages": [HumanMessage(content=user_input)]}, config=config
)
```

这一步传入两类信息：

- `HumanMessage` 是本轮新增状态；
- `thread_id` 告诉 checkpointer 这次调用属于哪段会话。

图运行完成后，`result["messages"]` 不只是最终文本，而是包括用户消息、模型 Tool 请求、Tool 结果和最终模型消息的完整序列。`_format_tool_events()` 从其中提取可观察轨迹，`run_turn()` 则寻找最后一条不含 `tool_calls` 的 `AIMessage` 作为最终答案。

### 2.3 为什么一次请求可能经过多次 LLM 调用

第一次调用 LLM 时，模型还没有计算结果和知识内容，所以它返回的是“动作请求”而不是最终答案。ToolNode 执行完成后，结果以 ToolMessage 进入状态。第二次调用 LLM 时，模型才拥有可引用的观察结果。

如果第二次判断仍需要另一项工具，循环可以继续；只要最后一条 AIMessage 仍含有 `tool_calls`，conditional edge 就会再次进入 ToolNode。

## 3. LangGraph 核心机制

### 3.1 State：Graph 运行时共同读写的数据

State 不是某个节点的局部变量，而是整个 Graph 在一次运行和多轮会话中共享的状态容器。EngiAgent 使用 LangGraph 预定义的 `MessagesState`，当前只需要一个核心通道：`messages`。

消息序列可以抽象为：

```text
[
  HumanMessage,
  AIMessage(tool_calls=...),
  ToolMessage,
  AIMessage(final answer)
]
```

工具结果之所以能够被下一次模型调用看到，不是因为 ToolNode 直接调用了 LLM，而是因为它把 ToolMessage 写入了同一个 State。

### 3.2 MessagesState：为消息合并准备好的 State

`MessagesState` 已定义消息累积规则。节点只需返回本次新增消息：

```python
return {"messages": [response]}
```

LangGraph 会把它追加到现有消息序列，而不是让 Agent 节点手工复制全部历史。对当前 MVP 而言，这比自定义包含大量字段的工程 State 更透明。

### 3.3 Node：一次可执行步骤

当前只有两个业务节点：

- `agent`：调用绑定了 Tool schema 的 ChatDeepSeek；
- `tools`：执行 AIMessage 中声明的 Tool 调用。

Node 不是“一个 Agent”。它只是 Graph 上一次状态变换。`agent` 节点读取 messages，新增 AIMessage；`tools` 节点读取 tool_calls，新增 ToolMessage。

### 3.4 Edge：执行顺序

Edge 决定节点之后去哪里。当前有两条固定边：

```text
START → agent
tools → agent
```

第一条保证输入先交给模型判断；第二条保证 Tool 的输出必须回到模型，而不是直接展示为最终答案。

### 3.5 Conditional edge：根据运行结果选择路径

`agent` 之后的路径不能预先固定，因为模型有时需要工具，有时只需聊天。当前代码使用：

```python
builder.add_conditional_edges("agent", tools_condition, ["tools", END])
```

`tools_condition` 检查最后一条 AIMessage 是否存在 `tool_calls`：

- 存在：进入 `tools`；
- 不存在：进入 `END`。

因此，“普通聊天不强制用 Tool”不是 CLI 中写死的关键词规则，而是 Graph 根据模型输出选择分支。

### 3.6 ToolNode：执行者，不是决策者

`ToolNode(TOOLS)` 持有可用 Tool。它负责读取 tool call 的名称和参数，匹配 Python Tool，执行函数，再构造与 `tool_call_id` 对应的 ToolMessage。

它不决定应调用哪个 Tool，也不负责将结果写成自然语言。这两个职责仍属于 LLM。

### 3.7 START 与 END：边界而非业务节点

`START` 表示一次 Graph invocation 的入口；`END` 表示本轮已经得到无需继续执行 Tool 的模型消息。它们用于描述控制边界，不执行领域逻辑。

### 3.8 当前 Graph 的完整代码为何这么短

```python
builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(TOOLS))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition, ["tools", END])
builder.add_edge("tools", "agent")
```

这六行已经表达了当前全部工作流。MVP 的重点是让循环清楚，而不是通过增加节点表现复杂度。

## 4. ReAct 是如何落到当前代码里的

ReAct 可以概括为 Reason、Act、Observation，然后基于观察继续 Reason。它在当前系统中的映射是：

| ReAct 阶段 | EngiAgent 中的实际载体 |
|---|---|
| Reason | Agent Node 中的 ChatDeepSeek 根据 system prompt 和 messages 判断下一步 |
| Act | AIMessage 中产生结构化 `tool_calls` |
| Observation | ToolNode 执行 Python Tool，生成 ToolMessage |
| Reason again | 固定边把 ToolMessage 带回 Agent Node |
| Final | 模型返回不含 tool_calls 的 AIMessage，Graph 进入 END |

这里需要区分两个容易混淆的概念：

- **ReAct 是工作范式**：推理、行动、观察、再推理；
- **LangGraph 是控制框架**：保存状态并确保节点按边循环。

LangGraph 不替模型做语义判断，ReAct 也不规定必须使用 LangGraph。EngiAgent 只是用显式 Graph 把这个范式实现得可读、可测试。

当前系统也不会把模型的隐藏思维过程打印出来。“Reason”在工程含义上指模型根据上下文作出的下一步决策，不要求暴露内部推理文本。

## 5. `bind_tools` 到底做了什么

### 5.1 它没有把 Python 函数塞进 DeepSeek

Tool 通过 `@tool` 获得名称、描述和参数 schema。`bind_tools(TOOLS)` 将这些结构化描述附加到模型请求，使模型知道“有哪些动作可以请求”以及“参数应采用什么形状”。

当前代码是：

```python
model_with_tools = model.bind_tools(TOOLS)
```

真正的数据流是：

```text
Python Tool
  │ @tool 读取函数名、docstring、类型注解
  ▼
Tool schema
  │ bind_tools 附加到模型请求
  ▼
DeepSeek
  │ 只返回调用意图，不执行 Python
  ▼
AIMessage.tool_calls
  │
  ▼
ToolNode 匹配名称并传入参数
  │
  ▼
Python function execution
  │
  ▼
ToolMessage
  │ 作为 observation 回到 messages
  ▼
DeepSeek 解释结果或选择下一步
```

例如模型可能产生近似下面的结构：

```python
{
    "name": "calculator",
    "args": {"expression": "12.5 * 8"},
    "id": "...",
}
```

这只是请求。直到 ToolNode 收到它，`calculator()` 才会在本地 Python 进程中运行。

### 5.2 Tool 描述为什么重要

模型看不到函数体，只能依靠名称、描述和参数 schema 选择 Tool。模糊描述会导致错误选择或错误参数。当前两个 Tool 的 docstring 分别明确了数学运算边界和 demo 知识查询边界，这也是 Tool 设计的一部分，而不只是注释。

## 6. 两个 Tool 为什么这样设计

### 6.1 calculator：把精确性移出语言模型

`calculator` 没有直接使用 `eval()`，而是先把表达式解析为 AST，只允许数字、括号和有限的算术运算符，并限制表达式长度、指数和结果范围。

这种设计解决两个问题：

- **确定性**：相同表达式得到相同程序结果；
- **安全边界**：用户不能借表达式执行导入、文件访问或任意 Python 代码。

当前实现仍是教学计算器，不处理单位制、符号计算、矩阵、误差传播或工程公式验证。未来的工程 Tool 应继续保持同样原则：输入经过校验，计算由程序完成，输出带有明确结构和边界。

### 6.2 get_demo_knowledge：先验证接口，再升级检索能力

知识 Tool 当前读取 `knowledge/demo_knowledge.md`，按 Markdown 二级标题分段，再用英文词项和中文二元片段进行简单打分。它没有 embedding、向量数据库或语义检索。

这看似简单，却验证了一个关键接口：

```text
自然语言查询 → 知识工具 → 有来源的文本片段 → LLM 解释
```

将来内部实现可以替换成：

- 工程规范数据库；
- PDF 分段检索；
- RAG；
- Web Retriever；
- 带版本、条文号和适用条件的规范服务。

只要 Tool 仍然接受清晰查询并返回带来源的结果，上层的 Agent → Tool → Agent 循环不必重写。需要变化的是 Tool 的能力和返回协议，而不是为了“接入 RAG”重新设计整个 Agent。

## 7. Memory 是如何工作的

### 7.1 三个部件必须同时存在

短期记忆由三部分共同完成：

```text
MessagesState     保存消息结构
InMemorySaver     保存每个检查点
thread_id         标识属于哪段会话
```

编译 Graph 时：

```python
return builder.compile(checkpointer=checkpointer or InMemorySaver())
```

每轮调用时：

```python
config = {"configurable": {"thread_id": self.thread_id}}
```

第一次使用某个 `thread_id` 时，checkpointer 保存本轮结束后的 State。第二次使用相同 `thread_id` 时，LangGraph 先恢复旧 State，再合并新的 HumanMessage。因此模型可以在 messages 中看到“项目跨度是 6m”。

### 7.2 `thread_id` 不同会发生什么

换一个 `thread_id` 等于开启另一段会话。两个 thread 的消息不会自动互通。这正是短期 conversation memory 的边界。

### 7.3 当前 memory 不是什么

`InMemorySaver` 的数据只存在于当前 Python 进程内。程序退出后不会写入数据库或文件。因此它不是：

- 跨进程持久化；
- 长期用户画像；
- 工程项目数据库；
- 可检索的知识记忆；
- 多用户权限系统。

当前实现足以演示多轮对话，但不能承担真实项目的数据管理。

## 8. 当前系统中什么是“AI”，什么不是

| 部件 | 主要职责 | 是否由模型生成结果 |
|---|---|---|
| ChatDeepSeek | 理解意图、选择 Tool、整合和解释结果 | 是 |
| calculator | 解析并执行受限算术表达式 | 否，Python 确定性执行 |
| get_demo_knowledge | 读取本地文件并匹配段落 | 否，规则检索 |
| LangGraph | 保存 State、路由节点、控制循环 | 否，流程框架 |
| ToolNode | 分发并执行模型请求的 Tool | 否，执行框架 |
| CLI | 接收输入、展示轨迹和答案 | 否，交互界面 |
| demo_knowledge.md | 提供外部知识内容 | 否，静态数据源 |
| InMemorySaver | 按 thread 保存 Graph 状态 | 否，内存存储 |

因此，“Agent 会计算”更准确的说法是：“Agent 能判断何时请求计算器，并能基于计算器结果作答。”这种表述在工程系统中很重要，因为它明确了结果的责任来源。

## 9. 当前架构的边界和不足

当前版本尚未实现：

- Streamlit 或其他 Web UI；
- RAG 和向量数据库；
- 工程规范数据库及条文版本管理；
- 结构、岩土或 SHM 计算引擎；
- 参数单位和量纲系统；
- 持久化长期 memory；
- verification / reflection；
- report generation；
- 真实工程 workflow；
- 工程结果的结构化 artifact 状态；
- Tool 权限、超时、重试和审计策略。

另外，Tool 是否被正确选择仍依赖模型、system prompt 和 Tool 描述。现有测试能够证明当前五个示例成立，却不能推出所有自然语言变体都能稳定路由。

这不是要隐藏的缺陷，而是 MVP 的实验边界：它已经证明循环可运行，但尚未证明工程能力可靠。

## 10. 将来加入第一个真实工程场景时怎么扩展

无论第一个场景是结构设计、岩土设计还是 SHM，建议先增加四类能力，而不是重写 Agent 循环。

### 10.1 Domain knowledge

建立带来源、版本和适用范围的领域知识。真实规范查询不能只返回一段文本，还应返回规范名称、版本、条文号、适用条件和检索证据。

### 10.2 Deterministic engineering tool

把核心计算写成普通、可单元测试的 Python 函数，再用 `@tool` 暴露给 Agent。例如一个简支梁场景可以先实现经过验证的输入 schema、单位转换和内力计算，而不是让 LLM 生成计算过程。

### 10.3 Validation tool

验证应成为独立步骤：检查缺失参数、单位、范围、边界条件、材料属性和模型引用关系。计算成功不等于输入合理。

### 10.4 Structured output

真实工程 Tool 应优先返回结构化结果，例如：

```text
input assumptions
units
calculation result
validation status
warnings
source/version
```

结构化结果随后可以被 LLM 解释、被测试断言、被报告模块消费。若所有信息只存在于一段自然语言里，后续校核会非常困难。

### 10.5 哪些部分可以保持不变

最初仍可以保留：

```text
START → agent → tools → agent → END
```

真正需要扩展的是 Tool 集合、Tool 输入输出、领域知识和 State 内容。只有当任务出现明确的审批、中断、并行或阶段门控需求时，才有理由增加 Graph 节点。

## 11. 核心 insight

EngiAgent 当前最重要的 insight 不是“LangGraph 可以画流程图”，而是：**模型不需要拥有每项能力，它需要知道何时把工作交给可靠的能力边界。**

第二个 insight 是：**Tool 调用不是一次函数调用的包装，而是一段消息协议。**模型提出结构化调用，ToolNode 执行，ToolMessage 返回观察，模型才有依据完成回答。

第三个 insight 是：**工程 Agent 的演进重点应是增加可验证能力，而不是增加 Agent 数量或 Graph 复杂度。**只要接口清楚，一个简单循环也可以编排越来越专业的工具。

## 12. 读完后应该能解释什么

读完本文后，应该能够解释：

1. 为什么工程问题不能默认只调用一次 LLM；
2. `MessagesState` 中依次保存哪些消息；
3. Agent Node 和 ToolNode 的职责差异；
4. conditional edge 如何让普通聊天直接结束、工具任务进入循环；
5. ReAct 的 Reason、Act、Observation 在代码中分别对应什么；
6. 为什么 `bind_tools` 不等于让 DeepSeek 执行 Python；
7. ToolMessage 为什么必须再次进入 Agent Node；
8. `InMemorySaver` 与 `thread_id` 如何共同实现多轮记忆；
9. 当前哪些结果来自 AI，哪些来自确定性程序；
10. 加入真实工程任务时应优先扩展哪些边界，以及为什么暂时不必重写 Graph。
