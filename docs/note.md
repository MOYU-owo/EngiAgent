# 个人Agent 基础知识体系存档

[toc]

-----------------------------------------2026.10.18-------------------------------------------------



## 1. LLM 与 Agent：基本概念、工作范式及应用动机

### 1.1 LLM 的基本原理与能力边界

### 1.2 Agent 的定义及其与普通 LLM 应用的区别

### 1.3 ReAct：Agent 如何通过推理与工具调用完成任务

### 1.4 Agent 与固定工作流的区别及适用边界

### 1.5 为什么考虑使用 Agent 完成钢筋混凝土构件设计任务

---



## 2. Agent 的系统架构与 LangGraph 实现

### 2.1 Agent 与开发框架的关系：不依赖框架如何实现最小 Agent

### 2.2 LangChain 与 LangGraph 的定位及区别

### 2.3 LangGraph 的核心组成与执行模型

- Graph、State、Node、Edge、Conditional Edge
- Tool 与 ToolNode 的关系
- Checkpointer 的作用
- Graph 的编译、执行与节点调度
- ReAct 循环如何映射到 Graph

----



## 3. EngiAgent 的运行机制：从用户输入到模型响应

### 3.1 执行入口：用户消息如何进入 Graph

- `run.py` 如何启动程序
- `graph.invoke()` 的作用与输入
- Graph 如何开始执行 Agent Node

### 3.2 模型调用：Agent Node 如何生成响应

- Agent Node 如何读取 `MessagesState`
- `bind_tools()` 如何向模型提供工具信息
- 模型如何决定直接回答或请求调用工具

### 3.3 工具调用：从 `tool_calls` 到执行结果

- `AIMessage` 与 `tool_calls` 的关系
- `tools_condition` 如何进行条件路由
- `ToolNode` 如何选择并执行具体工具
- `ToolMessage` 如何返回模型，形成 ReAct 循环

### 3.4 状态流转：消息如何在 Graph 中保存与更新

- `MessagesState` 的结构与作用
- `HumanMessage`、`AIMessage`、`ToolMessage` 的区别
- Node 的返回值如何更新 State
- 一次 `invoke()` 内部的多节点执行与终止条件

### 3.5 多轮对话：不同 `invoke()` 如何共享历史信息

- `thread_id` 的作用
- Checkpointer 如何保存和恢复状态
- 相同与不同 `thread_id` 的执行区别
- 多轮对话记忆的实现机制与限制