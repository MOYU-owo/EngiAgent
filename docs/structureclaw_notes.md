# StructureClaw：从一句工程需求到可追溯的计算结果

> 一份沿着任务执行过程展开的技术讲义<br>
> 面向了解 LLM、Agent、Tool、ReAct 和 LangGraph 基本概念，但尚未阅读大型 Agent 项目源码的读者。<br>
> 整理日期：2026 年 10 月 13 日。

这份讲义围绕一个问题展开：**StructureClaw 怎样把一个普通 LLM，接入工程知识、工程工具和计算程序，完成结构工程任务？**

全文跟随同一个两层钢框架请求。我们先走完一次任务，再回到过程中遇到的障碍：信息怎样补齐，模型怎样保存，下一步由谁决定，计算在哪里发生，结论又如何留下依据。每个技术对象都在它开始发挥作用的位置出现。

本文依据公开仓库中可读取的文档和实现整理。标为“源码节选”的内容保留真实标识；标为“教学示意”或“伪代码”的内容用于解释机制，不能直接当作运行输入。本文没有实际运行 StructureClaw，调用轨迹是源码关系的还原，不包含虚构的求解数值。上游链接指向持续变化的 master 分支，不是冻结的版本存档。

## 阅读导航

- [第 0 章：读懂 StructureClaw 前的最小先验](#chapter-0)
- [第 1 章：用户说“帮我分析这个结构”，究竟要求系统完成什么？](#chapter-1)
- [第 2 章：信息不完整时，Agent 凭什么知道该问什么？](#chapter-2)
- [第 3 章：怎样把描述变成所有工具都能使用的结构模型？](#chapter-3)
- [第 4 章：工具已经准备好，谁决定下一步做什么？](#chapter-4)
- [第 5 章：一次“运行分析”，怎样真正启动工程计算程序？](#chapter-5)
- [第 6 章：有了计算结果，怎样形成可以复核的结论？](#chapter-6)
- [第 7 章：回看整个任务，StructureClaw 为普通 LLM 补上了什么？](#chapter-7)

<a id="chapter-0"></a>

## 第 0 章：读懂 StructureClaw 前的最小先验

### 0.1 LLM、Agent 与 Tool：判断怎样变成动作

假如你问 LLM“这座框架怎样计算”，它可以生成一段说明。若系统还向它提供工具描述，它也可以生成调用请求，例如要求某个工具执行静力分析。但请求只有被程序接收和执行，才会产生计算结果。

这里，LLM 是生成判断、文字和调用请求的模型；Tool 是带有名称、参数约定和执行逻辑的动作接口；Agent 则是组织模型、工具、反馈与任务状态的系统。本文说“Agent 运行分析”，指的是这一套协作过程。

```text
Agent 系统
  |
  +-- LLM：根据上下文生成回答或调用请求
  |
  +-- Tool：接收参数，执行动作，返回反馈
  |
  +-- 状态与执行流程：保存进展，把反馈交回模型
```

知道这层关系，后面就能分别追问两件事：模型为什么选择这个动作，以及程序究竟执行了什么。

### 0.2 ReAct、LangGraph 与 State：多步任务怎样接起来

ReAct 描述一种推进方式：根据已有信息判断，执行动作，观察反馈，再作判断。LangGraph 提供组织这类执行过程的框架。其中，Node 是执行单元，Edge 决定执行接下来转向哪里，State 保存步骤之间需要传递的信息。

可以把一次执行理解为“某个 Node 读取 State，完成工作并返回更新，再沿 Edge 转向下一个 Node”。State 中既可以有聊天消息，也可以有结构模型。后文的 shared state，就是这些节点共同使用的任务状态，不是所有用户共享一份全局数据。

这几个概念属于不同层次：ReAct 说明循环方式，LangGraph 承载流程，Node 和 Edge 定义执行关系，State 承载任务数据。它们共同解释一次对话为什么能够跨过多个程序步骤。

### 0.3 Tool、Runtime 与 Solver：调用之后还有什么

工具暴露给模型的入口可以很小，例如“运行静力分析”。入口背后却需要选择分析能力、准备参数、进入 Python 环境、调用计算引擎并处理返回值。这些组织执行的代码，在本文中称为 Runtime。

Solver 是具体数值求解器，例如 OpenSees。Runtime 把输入送到适用的程序，Solver 根据模型完成数值计算，再沿调用路径把结果送回来。

```text
Tool 接口 --> Runtime 组织执行 --> Solver 数值求解
           <-- 结构化结果或错误 <--
```

后文遇到“工具调用成功”时，需要继续看它意味着请求被接收、程序被运行，还是分析本身确实得到有效结果。

### 0.4 普通 Agent 与工程 Agent：专业要求落在哪里

通用 Agent 也可能调用程序、维护状态和验证结果。工程任务的特别之处，在于这些机制必须对应明确的专业对象：单位、节点连接、材料、荷载、建模假设，以及校核的适用范围。

| 通用机制 | 在本讲义中的工程含义 |
|---|---|
| 理解用户需求 | 区分结构形式、分析目标和缺失条件 |
| 保存任务状态 | 保存工程草稿、结构模型与分析产物 |
| 执行工具 | 建模、验证、求解和规范校核 |
| 解释结果 | 说明数值对应的对象、条件和依据 |

所以，接上一个计算引擎只是其中一步。整个系统还要保证引擎收到有意义的输入，并让用户能够理解计算输出。这就是接下来七章要逐步展开的内容。

<a id="chapter-1"></a>

## 第 1 章：用户说“帮我分析这个结构”，究竟要求系统完成什么？

### 1.1 先明确什么叫完成任务

全文使用下面这个请求，场景改编自项目 README。为便于讨论，两个方向各按一跨空间框架理解；如果真实请求没有明确这一点，系统应先确认。

> 建一个两层钢框架，X、Y 方向各一跨，跨度分别为 6 米和 4 米，层高 3.6 米，采用 Q355 钢材，楼面恒荷载 5 kN/m²、活荷载 2 kN/m²。用 OpenSees 做静力分析，按适用的钢结构规范校核，并生成简短报告。

用户要的交付包含几种不同对象。结构模型记录“算了什么”，分析结果记录“程序算出了什么”，校核结果记录“检查了哪些要求”，报告把它们组织成读者能够复核的说明。只生成一段分析建议，尚未交付这些对象。[场景来源：项目 README][readme]

```text
需求 --> 工程草稿 --> 结构模型 --> 验证 --> 分析 --> 校核 --> 报告
          缺什么？    表达什么？   能否用？  响应如何？ 是否满足？ 依据在哪？
```

上图先列出任务依赖。实际执行可能在追问、修正和失败处理之间往返；后面看到的 Graph 决定这些动作如何被调度。

### 1.2 从一句自然语言到一次工程计算，StructureClaw 中间发生了什么？

这句话表达了目标，但还不是完整的计算输入。梁柱截面、柱脚约束等条件尚未明确，系统需要先整理已有信息，再补齐影响建模的关键条件。我们就跟着这个请求，看看它经过哪些软件对象，最终怎样到达计算程序。

请求首先作为用户消息进入 **State**。State 是 LangGraph 管理的结构化状态，既保存对话，也保存工程草稿、结构模型和分析结果。不同步骤通过它共享数据，因此这里的 shared state，指的是各个执行步骤共同使用的任务状态。

只保留与本例有关的字段，请求刚进入时可以这样理解：

```javascript
// 简化 State 快照，值为教学示意
{
  messages: [用户请求],
  draftState: null,       // 尚未整理工程条件
  model: null,            // 尚未建立结构模型
  analysisResult: null   // 尚未计算
}
```

这些字段对应源码中的真实状态对象；后面建模与分析工具会分别写入 model 和 analysisResult。[状态定义][state]

接下来，请求进入 **Agent Node**。Node 是图中的执行单元，Agent Node 的工作是读取当前状态、组织模型上下文并调用 LLM。LLM 结合领域 Skill 提供的指导，以及当前可用工具，判断接下来应识别结构类型、提取参数，还是提出问题。

需要执行动作时，模型的返回消息会包含 **tool_calls**：一组结构化调用请求，记录工具名称、参数和调用标识。它们随后交给 **ToolNode**，由这个负责工具执行的节点调用相应程序。

```text
用户输入 --> State.messages --> Agent Node
                                  |
                         返回消息有 tool_calls？
                            /             \
                           有              无
                           |               |
                           v               v
                       ToolNode        输出回答，结束本轮
                           |
                   执行工具，返回反馈
                   必要时更新 State
                           |
                           +-----> Agent Node
```

图中的箭头是 **Edge**，规定执行从哪个节点转向哪个节点。其中，Agent 后面的条件边检查是否存在 tool_calls；工具执行完后，则沿固定边回到 Agent。源码里的主图确实围绕这两个节点构建，可以压缩成下面的伪代码：

```python
# 只解释循环；实际状态更新由 LangGraph 管理
reply = agent(state)
while reply.tool_calls:
    state = tools_node(state, reply.tool_calls)
    reply = agent(state)
```

因此，“建模、验证、分析”是循环中执行的工程动作，并不各自占据一个独立 Graph 节点。[循环实现][graph]

回到框架请求。参数提取工具会整理跨度、层高、材料和荷载，逐步形成 draftState。如果发现关键条件不足，Agent 可以发起澄清；用户补充的信息经过再次提取后并入草稿。Skill 提供针对结构类型的处理指导和逻辑，使参数整理有具体的领域依据。

条件明确后，build_model 把草稿变成结构模型，并写入 State.model。模型用节点、构件、材料、截面和荷载等数据描述这座框架。随后调用 validate_model，就可以检查节点引用、几何和荷载等问题；错误或警告会成为下一轮判断的依据。

验证与分析工具都直接读取共享状态中的模型。LLM 无须在每次调用中重新抄写整份工程数据，只需提供本次动作需要的小量参数。假设模型已经准备好，相应分析能力也已启用，一次分析调用可以表示为：

```javascript
// 示意 tool_calls 中的一项，省略调用 ID
{
  name: "run_analysis",
  args: {
    analysisType: "static",
    analysisSkillId: "opensees-static"
  }
}
```

这条请求进入 ToolNode 后，才开始向工程执行层传递。下面按源码中的真实对象还原调用轨迹；它说明实际接线关系，不是本例的实测日志，也不预设计算成功：

```text
ToolNode 执行 run_analysis
  -> 从 State.model 读取模型
  -> AgentSkillRuntime.executeAnalysisSkill(...)
  -> 分析执行服务与 Python 运行时
  -> OpenSeesPy 调用 OpenSees
  <- 返回计算结果或错误
  -> 返回状态更新与工具反馈
  -> Agent Node 再次读取当前状态
```

这里的 **Runtime** 承接能力选择、输入传递和程序执行。它需要确认所选分析能力与请求匹配，并通过后端执行服务进入具体分析程序；如果运行条件不满足，调用会返回失败信息。

**Solver** 是完成数值求解的计算引擎。本例中，它是 OpenSees，Python 分析程序通过 OpenSeesPy 使用它。

| 对象 | 在本次分析中负责什么 |
|---|---|
| Agent Node | 调用 LLM，决定是否请求静力分析 |
| ToolNode | 找到并执行 run_analysis |
| Runtime | 将请求接入适用的分析程序 |
| Solver | 根据工程输入完成数值求解 |

正常获得返回值时，分析工具把完整结果写入 analysisResult，并返回较紧凑的 **ToolMessage**。ToolMessage 是工具反馈消息，让 Agent 知道本次调用的结果；完整工程数据继续保存在 State 中。入口检查直接拒绝请求或程序抛出异常时，并不意味着已经获得一份新的分析结果。[分析工具实现][tools]

Edge 随后把执行带回 Agent Node。它根据更新后的状态和反馈组织下一次模型调用：成功时继续处理已有结果，失败时说明问题或选择进一步动作。本例还要求校核和报告，所以得到分析结果后，任务仍要向这两项交付推进。

### 1.3 接下来沿着哪里深入

上面的预览同时出现了对话、数据和程序执行。后面每章只展开其中一个尚未讲透的问题：第 2 章追踪条件如何补齐，第 3 章解释模型如何表示与共享，第 4 章解释动作顺序，第 5 章进入真实计算，第 6 章把结果带到校核和报告。

先从最早发生的困难开始。用户没有给全参数时，系统究竟依据什么判断“还缺什么”？

<a id="chapter-2"></a>

## 第 2 章：信息不完整时，Agent 凭什么知道该问什么？

### 2.1 把“用户说过的话”整理成工程条件

“两层、层高 3.6 米”可以直接提取；“Q355”说明材料牌号，却没有给出梁柱截面。若把尚未确定的条件偷偷补成常见值，模型也许能够生成，但计算对应的工程已经悄悄发生变化。

因此，整理需求至少要区分三种情况。下面是对贯穿案例的教学整理，不是运行结果：

| 信息 | 当前含义 | 下一步 |
|---|---|---|
| 两层、X/Y 各一跨 | 用户明确说明的几何条件 | 提取并保留单位 |
| Q355 钢材 | 已知材料条件 | 转成建模所需的材料信息 |
| 梁柱截面、柱脚约束 | 请求中尚未明确 | 检查缺项，必要时追问 |
| 采用某种默认建模假设 | 可能的建议 | 让假设可见，并明确适用条件 |

并非所有字段都会触发同样的追问。哪些缺项会阻止当前阶段继续，要由对应结构类型的处理逻辑决定；不能仅凭这张教学表推断系统一定会问出某句话。

### 2.2 Skill 怎样参与，而不只是给 Prompt 加一段文字

StructureClaw 的 frame Skill 是一个领域能力包。它的声明告诉系统自己属于结构类型领域，能够参与意图识别、草稿提取、交互问题和模型构建。下面是声明中的少量真实字段：

```yaml
# 源码节选，省略其他字段
id: frame
domain: structure-type
capabilities:
  - intent-detection
  - draft-extraction
  - interaction-questions
  - model-build
  - report-narrative
```

这段声明使能力能够被发现，但实际行为还需要程序接线。frame 的 handler 中能看到提取草稿、合并状态、计算缺项和生成问题等方法；建模前也会检查执行阶段是否仍有关键缺项。[frame 声明][frame-manifest]、[frame handler][frame-handler]

可以用以下伪代码理解这组职责：

```python
patch = extract(user_message, current_draft)
draft = merge(current_draft, patch)
missing = compute_missing(draft, phase="execution")
if missing.critical:
    questions = build_questions(missing)
```

其中，自然语言理解帮助形成参数补丁，领域程序负责合并、检查和构造后续处理。阶段说明可以给模型提供指导，handler 则让部分要求落实为程序行为。读者因此应分别看“声明了什么能力”和“哪些代码实际执行了它”。

Skill 与 Tool 的关系也在这里变得具体：extract_draft_params 是 Agent 请求的动作；frame Skill 为这个动作提供框架问题的处理能力。同一个动作接口，可以在不同结构场景下接入不同领域逻辑。

### 2.3 追问怎样变成下一步真正可用的数据

假设系统需要确认柱脚条件，用户回答“柱脚按固定约束考虑”。这条回答先是对话中的新信息，必须经过提取与合并，才会进入工程草稿。

```text
extract_draft_params --> 返回关键缺项
          |
          v
ask_user_clarification --> 暂停并等待用户
          |
          v
收到回答 --> 再次 extract_draft_params
          |
          v
合并 draftState --> 重新检查缺项 --> 决定能否建模
```

当前工具通过 LangGraph 的 interrupt 发起澄清。提示规则还明确要求：收到回答后再调用参数提取工具，不能把“用户已经回答”视为“草稿已经更新”。这一点解释了对话与工程数据之间为什么需要转换步骤。[澄清工具][tools]、[提示构造与行为规则][prompt]

现在，任务拥有了逐步补齐的工程条件。下一步要把这些条件变成计算程序能操作的对象；“两层框架”将不再只是一句话。

<a id="chapter-3"></a>

## 第 3 章：怎样把描述变成所有工具都能使用的结构模型？

### 3.1 草稿与模型为何需要分开

工程草稿适合保留用户表达：有几层、几个跨度、采用哪种材料。求解程序需要的表达更明确：节点在哪里，构件连接哪些节点，每根构件使用哪个材料和截面，荷载作用在哪些对象上。

以“层高 3.6 米”为例，它会参与生成节点的位置；“X 方向一跨 6 米”会参与确定平面布置。建模工具将这类条件展开为 StructureModel。草稿便于继续沟通，结构模型便于后续验证、转换与执行。

```text
工程草稿                        StructureModel
两层、各向一跨         -->      节点及坐标
跨度与层高             -->      梁柱连接关系
材料与截面条件         -->      材料、截面及其引用
荷载与支承条件         -->      荷载工况、组合与约束
```

下面保留协议中的顶层字段，但将数组内容省略。空数组只是展示结构，不能拿来完成本例计算：

```json
{
  "schema_version": "1.0.0",
  "unit_system": "SI",
  "nodes": [],
  "elements": [],
  "materials": [],
  "sections": [],
  "load_cases": [],
  "load_combinations": []
}
```

这些字段组成共享的数据约定。不同工具按照同一约定解释模型，才不会各自对“节点”“材料”或“荷载组合”使用不同含义。[结构模型协议][reference]

### 3.2 验证解决的是哪一类错误

即使字段齐全，引用仍可能出错。设想某根梁连接节点 N1、N2，但节点表里只有 N1、N3；或者构件写了截面编号 S2，截面表却没有 S2。这些问题不依赖语言表达是否流畅，程序可以沿引用关系直接检查。

```text
构件 E1
  +-- 起点 N1 ------> 节点表：应存在 N1
  +-- 终点 N2 ------> 节点表：应存在 N2
  +-- 材料 M1 ------> 材料表：应存在 M1
  +-- 截面 S2 ------> 截面表：应存在 S2
```

这是验证机制的教学示意。StructureClaw 的 validate_model 从当前状态读取模型，通过验证能力返回错误或警告；它的接口说明覆盖连接、几何和荷载检查。[验证工具][tools]

检查通过的含义也有范围。字段、引用和部分工程条件能够被程序检查；用户是否准确描述了真实结构、支承假设是否合适，还需要在需求与模型之间复核。输入格式正确，是继续计算的基础，而非所有工程判断都已完成。

### 3.3 shared state 怎样减少步骤之间的数据搬运

如果每次分析都让 LLM 把模型从上一条消息复制到调用参数里，节点数一多，输入就会变长，漏字段或错编号也更难发现。StructureClaw 的做法是让工具从 State 读取完整工程对象，再把简短的执行反馈送回对话。

```text
                    shared State
                 +----------------+
build_model ---->| model          |----> validate_model
                 |                |----> run_analysis
run_analysis --->| analysisResult |----> run_code_check
run_code_check ->| codeCheckResult|----> generate_report
                 +----------------+
```

图中省略了消息字段。消息保存“发生了什么”，模型和结果字段保存“程序接下来使用什么”。State 还包含 artifacts，用来组织流水线产物；但讲解当前工具读写时，应以实际使用的 model、analysisResult 等字段为准，不把所有对象混成一个含糊的“记忆库”。[状态通道][state]

一次成功写回可以简化为：

```javascript
// 教学示意：字段对应源码，内容用占位符代替
{
  messages: [用户请求, 调用消息, 工具反馈],
  draftState: 已合并的工程草稿,
  model: 当前结构模型,
  analysisResult: 当前分析结果
}
```

共享状态也不自动保证数据永远有效。若用户改变跨度或截面，先前的分析结果是否仍对应当前模型，是必须重新判断的问题。读系统时，需要检查更新与失效逻辑，不能仅因这些对象都放在 State 中，就推断它具备完整的版本一致性保证。

有了可共享的模型，接下来的问题便是：谁来安排这些读写，避免在模型尚未准备好时就开始计算？

<a id="chapter-4"></a>

## 第 4 章：工具已经准备好，谁决定下一步做什么？

### 4.1 Agent Node 读到的并不是一份原封不动的 State

Agent Node 能访问程序状态，但 LLM 接收的是组装后的模型消息。系统提示构造器会把已选 Skill、草稿摘要、已有产物状态和会话配置组织成上下文，配合聊天历史和可用工具定义一起送给模型。

这一转换很重要。完整模型留给程序处理，摘要帮助 LLM 判断当前进度。例如“已有结构模型，但尚无分析结果”，足以帮助它选择分析动作，不必把所有节点重新展开在 Prompt 中。[上下文构造][prompt]

```text
State 中的草稿、产物状态 ----+
已选 Skill 的能力描述 ------+--> Agent Node 组织上下文 --> LLM
消息与工具反馈 -------------+
当前可用工具定义 -----------+
```

因此，LLM 选择下一步时，依赖的是经过组织的任务信息。摘要是否充分、反馈是否准确，也会影响它的判断。

### 4.2 Edge 决定转向，工程顺序来自多处约束

主 Graph 的真实接线很短：

```typescript
// 源码节选
.addNode('agent', callModel)
.addNode('tools', toolsNode)
.addEdge(START, 'agent')
.addConditionalEdges('agent', shouldContinue, ['tools', END])
.addEdge('tools', 'agent')
```

shouldContinue 检查最后一条模型消息有没有工具调用。它不会在这几行里判断“钢框架是否已经完成验证”。工程顺序还需要提示规则、工具前置检查和运行时条件共同约束。[Graph 接线][graph]

| 约束位置 | 本例中的作用 | 读源码时应如何理解 |
|---|---|---|
| 提示规则 | 要求先提取、建模、验证，再分析 | 指导模型选择动作 |
| 工具入口 | 没有 model 时拒绝分析 | 程序直接检查前置条件 |
| 分析运行时 | 选择兼容、已配置的分析能力 | 检查这次请求能否执行 |

例如，提示要求先验证，并不等于 Graph 用一条硬编码的边强制“验证节点只能进入分析节点”。准确地区分这几层，才能判断某个流程要求究竟靠什么落实。

### 4.3 ToolNode 怎样把一次动作接回循环

ToolNode 负责按照 tool_calls 找到并执行工具。StructureClaw 还在工具节点外加了一层包装：执行前把当前 Graph State 注入配置，供工具读取，并重新解析当前可用的工具集合。

工具完成后，可以返回 ToolMessage，也可以通过 Command 携带状态更新。下例只展示两类输出的关系：

```python
# 伪代码：省略真实协议字段
return Command(update={
    "messages": [ToolMessage(简短反馈)],
    "analysisResult": 完整分析结果
})
```

这解释了为什么工具执行以后，Agent 既能看到“刚才发生了什么”，后续工具又能读取完整结果。二者服务于不同接收者。

### 4.4 错误怎样改变下一步

把贯穿案例稍作变化：模型中存在两个荷载组合，但请求没有指定分析哪一个。分析工具包含相应检查，能够返回 LOAD_COMBINATION_REQUIRED，并列出已有组合。下面是根据检查逻辑编排的教学轨迹：

```text
请求静力分析
  -> 读取模型中的荷载组合
  -> 发现多个组合且未指定
  -> 返回 LOAD_COMBINATION_REQUIRED
  -> Agent 获得“需要选择组合”的反馈
  -> 补充选择后，才有条件再次请求分析
```

这比“发生错误，请重试”提供了更具体的信息。Agent 可以据此追问，但它是否正确追问、用户是否补齐条件，都需要后续交互，不能把返回错误等同于自动修复成功。[入口检查][tools]

至此，我们知道了动作怎样被选择与调度。下一章进入工具内部，追踪一次已经满足前置条件的分析请求。

<a id="chapter-5"></a>

## 第 5 章：一次“运行分析”，怎样真正启动工程计算程序？

### 5.1 先把“使用 OpenSees”落实为可执行能力

本例已经表达了 OpenSees 静力分析的意图，但系统仍需要把它对应到启用的分析 Skill。opensees-static 的声明把软件、分析类别和运行入口联系起来：

```yaml
# 源码节选，省略其他字段
software: opensees
analysisType: static
engineId: builtin-opensees
adapterKey: builtin-opensees
runtimeRelativePath: runtime.py
```

这几个字段回答了“调用哪一类实现”。声明还给出支持的模型类别和明确选择要求。它不会凭空安装求解器，也不能保证本地环境健康；能被发现、已经选中、能够执行，是需要分别确认的状态。[分析 Skill 声明][analysis-manifest]

Runtime 在这里是一组协作的执行代码：Skill runtime 负责能力选择和执行入口，分析服务承接分析请求，Python 侧继续处理引擎与模型。本文使用 Runtime 这个总称时，指的是这条运行链路。

### 5.2 请求如何跨过 TypeScript 与 Python 的边界

分析工具把 State.model 与分析参数送给 executeAnalysisSkill。后端提供本地分析客户端，客户端再调用 AnalysisExecutionService；后者把请求交给运行器。

```text
TypeScript 侧
run_analysis
  -> Skill runtime
  -> 本地分析客户端
  -> AnalysisExecutionService
  -> Python worker runner
             |
             | stdin：JSON 请求
             v
Python 侧
分析运行时 -> 对应分析实现 -> OpenSeesPy -> OpenSees
             |
             | stdout：JSON 返回值
             v
TypeScript 侧接收结果或错误
```

这里“本地客户端”值得注意。代码中即使出现 post('/analyze', ...)，也不必发生一次 HTTP 网络请求；本地客户端可以把路径映射为进程内服务调用。对外 API 和 Agent 内部调用能够复用相近的执行约定。[本地分析服务][analysis-service]

Python worker runner 则负责启动 Python 进程、发送 JSON、收集输出并处理超时等情况。跨语言边界采用结构化数据，成功返回含 ok 和 data，失败返回错误标识与说明。[进程通信实现][worker]

```javascript
// 返回协议示意，不是本例计算结果
{ ok: true, data: /* 分析输出 */ }
{ ok: false, errorCode: "...", message: "..." }
```

### 5.3 求解器真正计算的是什么

到达 OpenSees 前，分析程序还需要把统一结构模型转换成引擎理解的建模与分析操作。Solver 最终处理的是明确的数值对象：几何、单元、材料参数、约束和荷载。自然语言中的“Q355 钢框架”必须先经过这些表示步骤，才能参与求解。

| 执行位置 | 处理的问题 |
|---|---|
| Tool | 本次请求的分析类型与参数是什么 |
| Skill runtime 与分析服务 | 应进入哪个实现，请求是否满足调用条件 |
| Python 分析程序 | 怎样把工程模型转换为求解器输入并提取结果 |
| OpenSees Solver | 在给定模型与分析设置下求解结构响应 |

本讲义不展开有限元公式，因为这里要理解的是程序之间如何协作。不同引擎的输入转换、输出语义和运行依赖可能不同；PKPM、YJK 还需要相应本地软件与授权，因此更换引擎不能仅理解为替换一个名称。[引擎支持说明][readme]

### 5.4 返回值为什么还要经过整理

求解器返回数据后，上层程序需要把它们整理为系统可保存、可展示的分析结果。分析工具会构造反馈摘要，记录调用信息，并将完整结果写回 analysisResult。程序启动失败或入口条件不满足时，错误也沿工具路径回到 Agent。

此时应分清两种成功：通信成功说明收到了返回值，分析成功还需要检查结果本身的状态。用户真正关心的则更进一步：这些响应对应哪个模型、哪个荷载条件，能够支撑什么结论。

这正是下一章的起点。得到位移和内力以后，还需要把计算对象与校核依据连接起来。

<a id="chapter-6"></a>

## 第 6 章：有了计算结果，怎样形成可以复核的结论？

### 6.1 三类检查分别回答什么问题

如果程序输出了一组位移和内力，我们可以说获得了结构响应，但还不能仅凭“有数值”判断构件是否满足设计要求。分析与规范校核处理的是不同问题。

| 环节 | 主要检查对象 | 结论的范围 |
|---|---|---|
| 模型验证 | 数据结构、引用、几何及相关输入条件 | 模型在这些检查项上是否存在问题 |
| 数值分析 | 给定模型与工况下的求解过程和响应 | 是否得到分析结果，以及响应是什么 |
| 规范校核 | 模型、分析结果及适用规则所需信息 | 已执行校核项是否满足相应要求 |

本例要求按适用的钢结构规范校核，因此还需确定使用的规范能力和适用条件。一个工具支持某个规范名称，不能推出它覆盖该规范的全部条文、全部结构形式和全部设计场景。

### 6.2 校核如何使用已有模型和分析结果

run_code_check 从当前状态读取 model 与 analysisResult，再调用规范校核运行能力。代码校核执行服务把请求送入相应 Python worker。因而，规则程序可以依据明确的数据开展检查，LLM 则负责组织调用与解释反馈。[校核工具][tools]、[校核执行服务][code-service]

```text
State.model ----------+
                      +--> 规范校核运行时 --> 校核结果
State.analysisResult -+                         |
                                                v
                                      State.codeCheckResult
```

为了理解结果应当怎样被解释，可以看一个不带数值的教学记录。下列字段是阅读模型，不是仓库的原始返回 schema：

```text
对象：某根柱
依据：选定规范能力中的某项已实现检查
输入：这根柱的模型属性与相关分析结果
结果：满足 / 不满足 / 信息不足
范围：本次工况与本项检查
```

如果只保留一句“校核通过”，对象、依据和范围就都消失了。若某项未执行或信息不足，报告也应保留这一事实，不能把未检查的部分合并成肯定结论。

### 6.3 报告如何接上这条证据链

generate_report 同样读取已有状态，而非要求 LLM 从聊天记录中重建全部结果。当前实现会读取分析结果、校核结果、模型与草稿；缺少分析结果时，会返回需要先运行分析的错误。[报告入口][tools]

```text
工程条件与假设 ----+
结构模型 ----------+
分析结果 ----------+--> 报告能力 --> 报告产物
规范校核结果 ------+
```

这让报告生成拥有了确定的输入来源。报告中的自然语言负责解释数值含义、指出需要关注的对象，并说明限制；支撑结论的模型与计算产物仍应能够被找到。

用户可以沿着一条具体结论向前复核：它对应哪个构件，来自哪个校核项，使用哪份分析结果，分析又采用什么模型与荷载条件。这条追溯路径比报告文字是否流畅，更能说明交付是否充分。

### 6.4 trace 与工程正确性各自说明什么

仓库的运行约定包含 traceId、调用记录和耗时等信息，分析与校核代码也携带相关追踪元数据。这些信息帮助定位一次执行：哪项工具运行了，花了多久，结果来自哪次调用。[运行结果约定][reference]

但 trace 记录了一次执行，不会自动证明建模假设正确或规范覆盖完整。阅读报告时，要同时保留“发生过哪些程序动作”与“这些动作足以支持哪些工程判断”两个问题。

到这里，本例已经从需求走到了交付：有整理后的条件、可计算的模型、分析与校核产物，以及组织这些依据的报告。最后再把各个环节放回完整系统，看看它们为何需要这样的分工。

<a id="chapter-7"></a>

## 第 7 章：回看整个任务，StructureClaw 为普通 LLM 补上了什么？

### 7.1 把沿途出现的对象放进一张架构图

前面的章节沿任务前进。现在看整体架构，每个组件都能对应一个已经见过的用途：

```text
用户：工程描述、补充条件、查看结果
                  |
                  v
         前端工作区 / 聊天界面
                  |
                  v
          后端 API 与会话服务
                  |
                  v
+-------------- LangGraph ----------------+
|                                        |
| Agent Node -- tool_calls --> ToolNode  |
|      ^                          |      |
|      +-------- 工具反馈 --------+      |
|                                        |
|  shared State                          |
|  messages / draftState / model          |
|  analysisResult / codeCheckResult       |
|  report / artifacts                    |
+------------------+---------------------+
                   | 工具调用
                   v
       Skill runtime 与后端执行服务
          |              |             |
        建模/验证       分析运行时      校核/报告
                          |
                          v
                 Python / 引擎适配
                          |
                          v
                    Solver 求解
                          |
                   结果沿调用链返回
```

图中的纵向箭头表示调用关系；结果通过工具反馈和状态更新回到 Graph。Skill 既提供领域指导，也可以绑定执行能力，所以它的影响并不限于求解前的某一个步骤。

前端让用户补充条件、查看过程与产物；会话服务把用户交互接到 Agent 执行；Graph 组织循环；状态让工具共享工程对象；底层运行时把动作落实到程序。这些分工共同形成了可持续交互的工程工作区。[架构入口][architecture]

### 7.2 为什么还需要会话保存与过程展示

用户可能在一次追问后离开，也可能在计算结束后回来看报告。此时，单轮函数调用的返回值不够用：系统还需要保存会话与执行状态，并向界面展示工具进展和产物。

StructureClaw 使用会话记录和文件 checkpointer 支撑相关持久化，并通过流式输出把执行过程送到界面。checkpointer 可以理解为 Graph 状态的保存机制，用于后续恢复或继续执行。[会话与状态保存][architecture]

这不意味着任何失败都能自动从原地恢复。外部求解器运行到了哪里、重复调用会不会重新计算，以及产物是否仍可用，仍取决于具体执行路径。持久化解决“状态怎样留下来”，外部程序恢复则有自己的条件。

### 7.3 怎样判断系统的能力边界

读仓库时，容易把目录里存在的能力等同于主流程已经可用的能力。项目专门用运行状态区分这两者：

| 状态 | 阅读时应怎样理解 |
|---|---|
| active | 已接入主要执行路径 |
| partial | 已有部分接线，仍不完整 |
| discoverable | 能在能力目录中被发现，不等于自动进入主流程 |
| reserved | 保留了分类位置，尚无对应内置能力 |

当前状态文档将结构类型、分析和规范校核列为 active，将验证和报告导出列为 partial；其他领域也有仅可发现或预留的情况。这个状态描述的是接线成熟度，不是某一真实工程算例的正确率。[能力状态说明][runtime-status]

公开材料对“未匹配 Skill 的通用回退”与“零 Skill 时能否执行工程工具”的描述存在不同口径。本文因此不把“没有 Skill 也能照常完成工程分析”作为结论；具体能否执行，应以当前版本的工具策略、能力绑定和返回错误为准。

### 7.4 回到开篇的请求

现在再读“两层钢框架，用 OpenSees 分析、校核并出报告”，应该能在一句话背后看到一组清楚的责任：

| 请求推进时遇到的问题 | 系统中承担它的机制 | 留下的对象 |
|---|---|---|
| 条件尚不完整 | 领域 Skill、提取与澄清工具 | 工程草稿 |
| 语言不能直接计算 | 建模与模型验证 | 结构模型及检查反馈 |
| 需要决定下一步 | Agent Node、Edge、ToolNode | 调用请求与工具消息 |
| 需要真实求解 | Runtime、分析程序、Solver | 分析结果 |
| 需要判断与交付 | 校核、报告及追踪机制 | 校核结果和报告 |

LLM 的理解与选择能力贯穿这些步骤，工程知识为任务提供约束和方法，程序则建立、检查和计算明确的数据对象。读懂 StructureClaw 的关键，是能够沿一次请求追踪这三者怎样交接，并在任意结论处指出它的输入与执行来源。

<a id="sources"></a>

## 参考与阅读依据

以下链接用于核对文中的对象和机制；正文已在相关段落给出对应入口。推荐先读项目概览和架构说明，再按感兴趣的机制查看实现。

- [项目 README][readme]：案例、任务链与引擎运行条件。
- [Agent Architecture][architecture]：主循环、工具、Skill 与会话执行的整体关系。
- [Reference][reference]：模型协议与结果可观察性字段。
- [Skill Loading Mechanism][skill-loading]：能力声明、加载与执行约定。
- [Skill Runtime Status][runtime-status]：哪些领域已经接入运行路径。
- [Graph][graph]、[State][state]、[系统提示][prompt]：执行、数据与模型上下文。
- [工程工具][tools]：建模、验证、分析、校核与报告的调用入口。
- [frame 声明][frame-manifest]、[frame handler][frame-handler]：领域能力与程序行为的配合。
- [OpenSees 静力分析声明][analysis-manifest]、[分析执行服务][analysis-service]、[Python worker][worker]、[校核执行服务][code-service]：执行边界。

[readme]: https://github.com/structureclaw/structureclaw
[architecture]: https://github.com/structureclaw/structureclaw/blob/master/docs/agent-architecture.md
[reference]: https://github.com/structureclaw/structureclaw/blob/master/docs/reference.md
[skill-loading]: https://github.com/structureclaw/structureclaw/blob/master/docs/schema/skill-loading.md
[runtime-status]: https://github.com/structureclaw/structureclaw/blob/master/docs/skill-runtime-status.md
[graph]: https://github.com/structureclaw/structureclaw/blob/master/backend/src/agent-langgraph/graph.ts
[state]: https://github.com/structureclaw/structureclaw/blob/master/backend/src/agent-langgraph/state.ts
[prompt]: https://github.com/structureclaw/structureclaw/blob/master/backend/src/agent-langgraph/system-prompt.ts
[tools]: https://github.com/structureclaw/structureclaw/blob/master/backend/src/agent-langgraph/tools.ts
[frame-manifest]: https://github.com/structureclaw/structureclaw/blob/master/backend/src/agent-skills/structure-type/frame/skill.yaml
[frame-handler]: https://github.com/structureclaw/structureclaw/blob/master/backend/src/agent-skills/structure-type/frame/handler.ts
[analysis-manifest]: https://github.com/structureclaw/structureclaw/blob/master/backend/src/agent-skills/analysis/opensees-static/skill.yaml
[analysis-service]: https://github.com/structureclaw/structureclaw/blob/master/backend/src/services/analysis-execution.ts
[worker]: https://github.com/structureclaw/structureclaw/blob/master/backend/src/utils/python-worker-runner.ts
[code-service]: https://github.com/structureclaw/structureclaw/blob/master/backend/src/services/code-check-execution.ts
