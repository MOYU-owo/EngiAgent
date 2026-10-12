# StructureClaw：一个工程 Agent 是如何真正运行起来的

## 0. 如何阅读这份笔记

这不是 StructureClaw 的安装教程，也不是按文件名排列的源码索引。它试图回答一个系统问题：**一个结构工程 Agent 为什么不能只是 LLM 加一段更长的 Prompt，StructureClaw 又怎样把工程能力拆进可执行系统？**

本文基于 2026 年 9 月 29 日重新检查的 StructureClaw `master` 分支。重点阅读了项目 README、Agent 架构与协议文档、LangGraph runtime、State、Tool registry、Skill loader、分析执行服务以及 Python worker 边界。仓库仍在演进，因此本文描述的是这次阅读时能从当前仓库确认的实现，不把路线图当作已实现事实。

阅读时建议区分三类陈述：

- **仓库事实**：README、文档或当前源码可以直接确认；
- **机制解释**：对代码如何协作的归纳；
- **本文 insight**：从 StructureClaw 提炼给 EngiAgent 的设计启发。

主要来源包括：[README](https://github.com/structureclaw/structureclaw)、[Agent Architecture](https://github.com/structureclaw/structureclaw/blob/master/docs/agent-architecture.md) 和 [Reference](https://github.com/structureclaw/structureclaw/blob/master/docs/reference.md)。

## 1. StructureClaw 到底想解决什么

### 1.1 普通 Chat LLM 为什么不等于工程设计 Agent

一个结构工程请求可能只有一句话：

> 建立两层钢框架，运行静力分析，按规范校核并生成报告。

但这句话背后不是一次文本补全，而是一组有前后依赖的工程动作：识别结构类型、提取尺寸和材料、补齐关键参数、建立结构化模型、检查几何和引用、选择分析引擎、运行求解、执行规范校核、保存结果并生成报告。

普通聊天模型可以解释这些步骤，却无法仅靠生成文本保证：

- 节点、构件、材料和截面引用一致；
- 荷载与单位正确；
- 求解器真正运行；
- 规范校核使用了分析结果；
- 最终报告可以追溯到输入和计算产物。

StructureClaw 的目标因此不是让 LLM “背会结构工程”，而是把 LLM 放进一个可执行、可观察、有状态的工程工作台。README 将其概括为：

```text
describe → draft model → validate → analyze → code-check → report
```

### 1.2 工程 Agent 真正困难在哪里

如果只看对话表面，系统似乎只是“用户说一句，Agent 回一句”。真正困难发生在对话背后：自然语言信息不完整，工程数据体量大，求解器有不同运行环境，结果需要验证，错误需要被诊断，多个步骤还必须共享同一份模型和中间产物。

所以 StructureClaw 的主要复杂度不是一个更复杂的 Prompt，而是建立了边界：

```text
语言决策边界
工程数据边界
领域 Skill 边界
可执行 Tool 边界
Python/商业软件运行边界
状态与持久化边界
```

## 2. 一句自然语言进入系统后发生什么

以 README 中的两层钢框架示例为背景，当前公开文档给出的目标执行链是：

```text
detect_structure_type
→ extract_draft_params
→ build_model
→ validate_model
→ run_analysis
→ run_code_check
→ generate_report
```

把它放回系统分层，可以得到更完整的数据流：

```text
Engineer
  │ 自然语言 + 可选附件/上下文
  ▼
Next.js workspace
  │ HTTP / streaming
  ▼
Fastify chat API
  │ 创建或恢复 conversation、trace、thread state
  ▼
LangGraphAgentService
  │ HumanMessage + session configuration
  ▼
LangGraph ReAct graph
  │
  ├─ Agent Node / LLM
  │    ├─ 理解意图
  │    ├─ 选择 Skill 上下文与 Tool
  │    └─ 产生 tool_calls
  │
  └─ Tool Node
       ├─ detect / extract / build
       ├─ validate
       ├─ analyze
       ├─ code-check
       └─ report
            │
            ▼
       Skill Runtime + execution services
            │
            ├─ Structure protocol Python worker
            ├─ Analysis Python worker
            │    ├─ OpenSeesPy
            │    ├─ PKPM/SATWE adapter
            │    └─ YJK adapter
            └─ Code-check Python worker
                 │
                 ▼
       structured artifacts / ToolMessage
                 │
                 └────────→ Agent Node
                                │ 解释结果或选择下一步
                                ▼
                      streamed answer + trace + report
```

这张图有两个关键点。

第一，LLM 发起 `run_analysis` 不等于 LLM 自己完成有限元计算。调用沿 Tool、Skill runtime、execution service 和 Python worker 进入具体引擎。

第二，所谓工程 pipeline 并不是七个固定 Graph 节点。当前主 Graph 仍然只有 Agent 和 Tools 两个核心节点；具体阶段表现为 LLM 在约束下选择的一系列 Tool 调用。

## 3. StructureClaw 的整体系统分层

### 3.1 前端：让工程过程可见

README 显示前端是 Next.js workspace。它承担聊天、配置、附件和结果展示，而不承担结构分析。前端的价值不只是“有一个网页”，还包括把 Tool 调用、模型草稿、验证结果、分析产物和报告暴露给用户。

### 3.2 API / Backend：产品边界与运行入口

Fastify backend 提供同步聊天、流式聊天、恢复会话和 Agent 执行入口，也提供 `/validate`、`/convert`、`/analyze`、`/code-check`、`/engines` 等工程接口。

这层将 UI、Agent 和工程 runtime 解耦：前端不需要知道 Python worker 的启动细节，Agent Tool 也可以通过本地 client 使用与 HTTP 路由相近的 contract。

### 3.3 Agent service：把一次请求变成一次可恢复执行

`LangGraphAgentService` 是主编排入口。当前源码可以确认它负责同步、流式和 resume 入口，创建或复用 conversation，组装 trace，并注入 Analysis、CodeCheck 和 StructureProtocol 的本地 client。Graph 构建后在进程生命周期内缓存，而不是每个 token 都重新构建。

### 3.4 LangGraph：控制循环

Graph 保存 State、执行节点、根据 tool_calls 路由，并通过 checkpointer 持久化。它不实现钢结构分析，也不理解某条规范的计算公式。

当前 `graph.ts` 最终仍构建下面五条关系：

```typescript
.addNode('agent', callModel)
.addNode('tools', toolsNode)
.addEdge(START, 'agent')
.addConditionalEdges('agent', shouldContinue, ['tools', END])
.addEdge('tools', 'agent')
```

来源：[backend/src/agent-langgraph/graph.ts](https://github.com/structureclaw/structureclaw/blob/master/backend/src/agent-langgraph/graph.ts)

### 3.5 Skill：领域能力包

Skill 使用 manifest 描述身份、domain、触发词、阶段、能力、兼容性和 runtime contract，并可携带 stage Markdown、handler 或 Python runtime。结构类型、分析类型、规范校核等都可以成为不同 domain 的 Skill。

### 3.6 Tool：LLM 可请求的动作

Tool registry 维护 Tool ID、分类、风险、默认启用状态、双语描述和 factory。当前可确认的工程 Tool 包括结构类型识别、参数提取、模型构建、模型验证、分析、规范校核和报告生成；此外还有计算、澄清、会话设置、memory、文件和 shell 等工具。

### 3.7 Engineering runtime：把 Tool 请求变成工程执行

工程执行并不全在 TypeScript 中完成。当前仓库通过 `PythonWorkerRunner` 启动 Python worker，将 JSON 请求写入标准输入，再从标准输出读取统一的成功或错误 envelope。

例如 Structure Protocol worker 处理 schema、模型验证和格式转换；Code Check worker 调用 Python `run_code_check`；Analysis runtime 根据 Skill manifest 和 engine registry 选择对应 runtime。

### 3.8 State / Persistence：让步骤共享同一工程对象

State 除 messages 外还保存 draft、artifacts、选中的 Skill、Tool 权限、locale、workspace、执行策略、provider binding 和结构类型等字段。文件 checkpointer 与 conversation 数据库负责比内存会话更完整的持久化边界。

## 4. LangGraph / ReAct 在里面到底承担什么

### 4.1 Graph 本身为什么仍然简单

`shouldContinue` 只检查最后一条消息是否存在 tool calls：有则去 `tools`，没有则结束。Tool 执行后固定返回 `agent`。

```text
START
  ↓
agent ── no tool_calls ──→ END
  │
  └── tool_calls → tools ──→ agent
```

因此 StructureClaw 不是靠几十个 Graph 节点表达工程专业性。Graph 只负责可靠重复 ReAct 循环。

### 4.2 复杂度实际在哪里

当前 `graph.ts` 已包含模型上下文压缩、消息协议修复、图像 ToolMessage 清理、Tool 调用次数限制、动态 Tool 策略和状态注入。这些都是围绕生产运行的防护，但工程语义仍主要在以下位置：

- draft 与 artifact 状态；
- Skill manifest 和 handler；
- Tool 生态；
- 结构模型 protocol；
- 分析/规范校核运行时；
- 引擎选择与依赖检查；
- checkpoint 和 conversation persistence。

### 4.3 ReAct 在系统里的位置

```text
Reason       LLM 根据消息、Skill 上下文和当前 artifacts 判断下一步
Act          生成 detect/build/validate/analyze 等 tool_call
Observation  ToolNode 返回 ToolMessage，并可能更新 artifact state
Reason again LLM 读取新状态与结果，决定继续 pipeline 还是作答
```

这说明 ReAct 是上层编排机制，不是工程求解方法。有限元求解、规范公式和模型验证依然属于工程程序。

## 5. Skill 和 Tool 为什么不是同一个东西

### 5.1 Skill 更接近“怎样完成一类领域任务”

以当前 beam Skill 为例，`skill.yaml` 明确声明它属于 `structure-type` domain，具有 intent detection、draft extraction、interaction questions、model build 和 report narrative 等能力，并覆盖 intent、draft、analysis、design 阶段。

它回答的是：

- 这是什么类型的工程问题？
- 需要哪些参数？
- 哪些信息缺失时应追问？
- 如何把这一类型映射成统一结构模型？
- 在分析或设计阶段应提供什么领域上下文？

结构类型 Skill 因而可以包含 manifest、阶段说明和 handler。分析 Skill 还会声明 software、analysisType、engineId、adapterKey 和 `runtime.py`。

### 5.2 Tool 更接近“现在执行一个动作”

`validate_model`、`run_analysis` 和 `generate_report` 是 LLM 可以调用的动作接口。Tool 有清晰输入 schema，执行后返回 ToolMessage 或更新 Graph State。

它回答的是：

- 现在要执行哪个动作？
- 参数是什么？
- 返回了什么结果或错误？

### 5.3 二者如何协作

```text
Skill: OpenSees static
  ├─ 描述何时适用
  ├─ 声明支持 static、frame/truss/generic
  ├─ 绑定 builtin-opensees adapter
  └─ 指向自己的 runtime.py

Tool: run_analysis
  ├─ 接收分析请求
  ├─ 从当前 State 取得 model/artifacts
  ├─ 让 Skill runtime 解析 provider
  └─ 调用 analysis execution service
```

因此，Skill 不是 Tool 的另一个名字。Skill 组织领域能力、选择策略和运行绑定；Tool 是 ReAct 循环中可执行的动作表面。

### 5.4 一个重要事实：Skill 是增强层，不是唯一入口

README 明确写明 Skills 是 enhancement layers，未匹配 Skill 时可以回退到 generic no-skill modeling。这说明 StructureClaw 没有把整个系统锁死在 Skill 命中上，而是允许基础对话和通用路径继续存在。

## 6. 哪些事情由 LLM 做，哪些事情由工程程序做

| LLM / Agent 层 | 工程程序 / runtime 层 |
|---|---|
| 理解自然语言意图 | 验证结构模型 schema 和引用关系 |
| 判断缺少哪些信息 | 构建或转换结构化模型 |
| 选择下一项 Tool | 运行 OpenSees、PKPM 或 YJK adapter |
| 组织多步调用 | 执行数值分析 |
| 根据结果解释和追问 | 执行规范校核规则 |
| 生成面向用户的叙述 | 返回结构化结果与错误信息 |

当前 Python worker 的通信形式进一步强化了这条边界：TypeScript runner 启动明确的 worker 文件，以 JSON 传入 action 和 input；Python 代码返回 `{ok, data}` 或结构化错误。模型不会进入 Python 进程替换求解逻辑。

对于 OpenSees，仓库文档确认运行依赖是 backend Python 环境中的 OpenSeesPy；PKPM 需要本地 SATWE/JWSCYCLE 和授权；YJK 需要本地 YJK 8.0、其 bundled Python 3.10 和授权。商业引擎不是仓库“模拟出来”的。

**机制解释：** LLM 的价值是把非结构化意图映射成受约束的调用序列；工程程序的价值是让每个关键结果具有可重复的执行来源。

## 7. 为什么 StructureClaw 要维护结构化状态

### 7.1 只靠聊天历史搬运模型会发生什么

真实结构模型包含节点、构件、材料、截面、荷载工况、组合和分析参数。若每次 Tool 调用都让 LLM 把整份 JSON 从上一条消息复制到下一组参数，会产生三个问题：

- token 成本和上下文长度快速增长；
- 模型可能漏字段、改 ID 或破坏引用；
- 中间产物难以被后续 Tool 和 UI 稳定读取。

### 7.2 当前 State 保存什么

`state.ts` 可以确认主要状态包括：

- `messages`：对话与 Tool 协议；
- `draftState`：累计的结构草稿参数；
- `artifacts`：按 kind 保存的 pipeline 产物；
- `selectedSkillIds`：当前选择的 Skill；
- `toolAccessPolicy`：Tool 和附件访问策略；
- `locale`、`workspaceRoot`、`policy`；
- provider bindings、last user message、structural type 等。

文档还明确指出，Tool 应从 State 读取 model、analysis、report 和 draft artifacts，而不是在 Tool 参数间传递大型序列化对象。

### 7.3 State 怎样进入 Tool

当前 Graph 在调用模型和工具前把 `agentState` 注入 `config.configurable`。工具节点还专门包裹了原始 ToolNode，以确保当前 Graph State 和动态 Tool policy 在执行前可见。

**本文 insight：** State 不只是 memory。它还是工程 workflow 的共享工作台，使多个 Tool 围绕同一组可验证 artifacts 协作。

## 8. 新增一个工程场景时大概要改什么

### 8.1 新增结构类型

应增加 `structure-type` Skill：manifest 描述触发、能力和结构类型，stage Markdown 提供领域步骤，需要执行逻辑时加入 handler，并让 draft/model builder 支持相应结构语义。

### 8.2 新增设计规范

应增加或扩展 `code-check` domain 的 Skill、规则和 Python runtime，并明确设计规范 ID、输入分析结果、适用材料/构件及输出校核项。若仅在 Prompt 中加入规范名称，无法形成可验证校核。

### 8.3 新增分析后端

分析目录的规则是“一种软件 × 一种分析类别 = 一个 Skill”。需要添加 `skill.yaml`、自己的 `runtime.py`、必要的阶段说明与 helper，并在 engine/adapter registry 中建立真实绑定。软件不支持的分析类型不应创建虚假 Skill。

### 8.4 新增 Tool

当需要新增 LLM 可主动请求的动作时，扩展 Tool implementation 与 registry，并定义名称、描述、schema、风险和默认启用策略。若能力只是现有 `run_analysis` 背后的新 provider，则未必需要新增一个同义 Tool。

### 8.5 新增 Skill domain

当前仓库已经区分 structure-type、analysis、code-check、data-input、load-boundary、material、section、validation、visualization 等 domain，但文档明确提醒各 domain 成熟度不同。新增 domain 需要同时考虑 catalog 可见性、runtime 接线和 artifact contract，不能把“目录存在”误写成“主流程已完整支持”。

## 9. 哪些设计值得 EngiAgent 借鉴

### 9.1 Graph 保持简单

工程能力增加后，仍可保留 Agent/Tool 两节点循环。只有控制语义真的不同，才增加节点。

### 9.2 工程计算与 LLM 解耦

LLM 产生调用意图，计算由可测试程序完成。EngiAgent 的 calculator 已经是这条原则的最小版本。

### 9.3 Tool 调用可观察

StructureClaw 的结果 contract 包含 trace、duration、metrics 和 toolCalls。EngiAgent 当前打印 Tool call/result，虽简单，但方向一致。

### 9.4 State 与对话分开理解

未来 EngiAgent 不应把工程模型只保存在自然语言消息中。应增加结构化 project/draft/artifact 状态，同时保留 messages 作为交互历史。

### 9.5 领域能力模块化

结构类型、分析 provider 和规范校核的变化速度不同。模块化可以避免增加一个工程场景就重写主 Agent。

### 9.6 Validation 是独立环节

建模完成不代表模型可计算，分析完成也不代表结果可用于设计。验证必须有自己的 contract、错误和测试。

### 9.7 Tool 不应搬运大型 artifacts

大型模型和结果由 State 保存，Tool 传递引用和小参数。这会减少 LLM 对工程数据的无意改写。

## 10. 哪些设计当前不应该照搬

### 10.1 完整 frontend/backend

EngiAgent 当前的学习目标是理解核心循环。引入 Next.js、Fastify 和流式协议会增加运行与调试面，却不会改善两个 demo Tool 的教学价值。

### 10.2 Database 与 production checkpointer

SQLite、conversation records 和文件 checkpointer适合产品运行；当前 CLI 用 `InMemorySaver` 已足以验证 thread-level memory。过早持久化会引出迁移、并发和数据生命周期问题。

### 10.3 Plugin / SkillHub 系统

动态安装、启停、冲突优先级和用户 Tool 加载适合已有大量能力的系统。EngiAgent 只有两个 Tool，此时直接 Python 注册更透明。

### 10.4 多分析引擎

OpenSees、PKPM、YJK 的依赖、授权、模型转换和结果语义都不同。第一个真实工程任务应先把一个确定性路径做对，而不是先抽象统一所有求解器。

### 10.5 Complex state protocol

StructureClaw 的 draft、artifact、binding、policy 和 workspace 状态来自真实产品需求。EngiAgent 在没有真实工程 artifact 前复制这些字段，只会形成空抽象。

### 10.6 Dynamic Skill registry

当前 MVP 尚未遇到能力发现和 provider 选择问题。先通过一个领域 Tool 学会输入验证、计算、测试和解释，再考虑 Skill 层更合理。

## 11. StructureClaw 对工程 Agent 的真正启发

### Insight 1：工程 Agent 的核心不是“让 LLM 会算”

真正目标是让 LLM 能可靠编排领域知识、确定性计算、验证、规范校核和报告。模型负责路线，程序负责证据。

### Insight 2：自然语言到工程结果之间必须有中间表示

draft、StructureModel 和 artifacts 将模糊描述逐步变成可检查对象。没有中间表示，系统只能在 Prompt 中反复猜测。

### Insight 3：验证不是计算失败后的补丁

`build_model → validate_model → run_analysis` 的顺序说明验证是 pipeline 的正式阶段。它阻止不完整模型进入昂贵或危险的下游执行。

### Insight 4：Graph 简单不代表系统简单

两节点 ReAct Graph 足以驱动复杂系统，因为专业性位于 State、Skill、Tool 和 runtime。增加 Graph 节点并不会自动增加工程可信度。

### Insight 5：可追溯性是工程 Agent 的产品能力

Tool 调用、输入、产物、错误、trace 和报告之间的关系，决定用户能否复核结论。最终答案写得流畅，不等于过程可信。

### Insight 6：扩展点必须对应稳定责任

新结构类型扩展 Skill，新动作扩展 Tool，新求解器扩展 provider/runtime，新中间结果扩展 artifact contract。边界稳定后，系统才能增长而不失控。

## 12. 当前阅读中无法确认的细节

本次可以确认 Python worker 的 JSON stdin/stdout contract、分析 Skill 的 `runtime.py` 约定，以及 OpenSees/PKPM/YJK 的引擎矩阵。但没有在本地安装或实际运行 StructureClaw，也没有商业软件授权，因此本文不对以下事项作实测结论：

- PKPM 和 YJK 在具体版本、许可及项目环境中的真实成功率；
- 所有 Skill domain 当前端到端成熟度；
- 所有结构类型在所有分析类型下的数值正确性；
- 生产环境的性能、并发和长期 checkpoint 恢复效果。

这些内容应通过仓库测试、实际引擎和目标工程算例验证，不能从目录结构推断。

## 13. 读完以后应该能够解释什么

读完本文后，应该能够解释：

1. 为什么普通 Chat LLM 不能自动成为工程设计 Agent；
2. 一句结构描述怎样进入 draft、model、validation、analysis、code-check 和 report 链路；
3. 为什么 StructureClaw 的主 Graph 仍然只有 Agent 和 Tools 两个核心节点；
4. Skill 与 Tool 的责任差异以及二者怎样协作；
5. 哪些决策由 LLM 完成，哪些结果由 Python runtime 或分析引擎产生；
6. 为什么大型结构模型和分析结果应放在 State/artifacts，而不是反复经过 Prompt；
7. 新增结构类型、规范、分析后端和 Tool 时分别要扩展哪一层；
8. 为什么 validation 是独立而必要的工程步骤；
9. StructureClaw 哪些设计值得 EngiAgent 学习；
10. 为什么完整前后端、数据库、SkillHub、多引擎和复杂状态暂时不适合 EngiAgent MVP。

## 参考入口

- [StructureClaw README](https://github.com/structureclaw/structureclaw)
- [Agent Architecture](https://github.com/structureclaw/structureclaw/blob/master/docs/agent-architecture.md)
- [Protocol Reference](https://github.com/structureclaw/structureclaw/blob/master/docs/reference.md)
- [LangGraph graph.ts](https://github.com/structureclaw/structureclaw/blob/master/backend/src/agent-langgraph/graph.ts)
- [Agent state.ts](https://github.com/structureclaw/structureclaw/blob/master/backend/src/agent-langgraph/state.ts)
- [Tool registry](https://github.com/structureclaw/structureclaw/blob/master/backend/src/agent-langgraph/tool-registry.ts)
- [Skill runtime](https://github.com/structureclaw/structureclaw/blob/master/backend/src/agent-runtime/index.ts)
- [Skill loader](https://github.com/structureclaw/structureclaw/blob/master/backend/src/agent-runtime/loader.ts)
- [Analysis skills](https://github.com/structureclaw/structureclaw/tree/master/backend/src/agent-skills/analysis)
- [Analysis execution service](https://github.com/structureclaw/structureclaw/blob/master/backend/src/services/analysis-execution.ts)
- [Python worker runner](https://github.com/structureclaw/structureclaw/blob/master/backend/src/utils/python-worker-runner.ts)
