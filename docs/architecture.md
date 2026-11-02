# EngiAgent 当前架构：仅 CN

更新：2026-11-02。所有命令行、网页和 Python 工程入口均使用中国规范引擎，旧教学公式及通用 ReAct Demo 已移除。

```text
结构化 CN 任务文件 ─────────────┐
自然语言 → DeepSeek Dispatcher ─┤
                              ↓
                  TaskRequest / CNParameters 校验
                              ↓
                   参数表 → 显式确认 → 确认哈希
                              ↓
               新设计 → Design 工程 DAG → 实配候选
                              ↓
                     Evaluation 独立工程 DAG
                              ↓
             请求项结果 + 依据 + 复用记录 + 修订历史
                              ↓
                       报告 / 界面 / 专家咨询
                              ↓
              修改建议 → 未确认草稿 → 再次确认并重算
```

## 数据与入口

`cn_schema.py` 统一定义 CN 请求、材料等级、适用边界、参数来源、工具结果、进度及状态。`TaskRequest.code` 只允许 `cn-2024`，默认也为 CN；目标只允许抗弯、抗剪、构造、裂缝和长期挠度。`EngineeringState.profile` 只接受 `CNProfile`。

`cn_workflow.py` 是唯一工作流，负责参数归一化、确认、修订、进度/计划校验、DAG 执行、缓存及有限改设。旧的通用工作流转发层已删除。

`run.py` 直接进入 CN 命令行；`streamlit_app.py` 启动工作台。两者调用同一套 `prepare`、`confirm`、`run_engineering`，不存在通过入口选择其他规范的路径。

## 模型与程序职责

`DeepSeekRoles` 从明确需求提取 CN 参数，并在全模型模式下返回受约束的工具计划。`ProgramRoles` 直接使用程序 DAG；`FixtureRoles` 用于明确标记的离线测试。三者共用相同的工程公式。

`consultation.py` 通过一次结构化请求理解问题或提取有原文依据的参数修改，再由程序展示已有工具结果与解释。建议绑定计算状态，采用后须重新确认。它不执行模型生成的公式或代码。

## 工具、依赖与缓存

`cn_tools.py` 保存唯一的计算工具注册表；`cn_outputs.py` 校验输出。`errors.py` 中的 `EngineeringFailure` 区分工程不可行和执行异常。

`dependency_graph.py` 声明各节点的输入字段、上游依赖、公式版本和目标映射。工具只接收声明输入。缓存依据输入、上游输出、公式版本及 CN 配置的哈希复用；失效节点重算，上游异常只阻断依赖分支。

设计候选经独立 Evaluation 按实配尺寸与配筋复核。既有梁不自动改配筋；有限改设仅用于已确认的新设计，受轮次和动作范围限制。

## 展示与结果

`cn_presentation.py` 统一提供 CN 字段名称、输入编辑、显示格式、规范报告以及中文 Markdown 与 JSON 保存。旧的展示及报告转发文件已删除。

`ui/service.py` 管理界面确认、调用审计和咨询；其余界面模块投影实际记录，保持完整精度计算、显示取整。机制实验仅比较同一 CN 内核下的全量、按目标、缓存三种执行方式。

支持范围和规范条文见 [任务与公式规范](rc_beam_cn_design_spec.md)，迁移和验证见 [CN 单体系说明](cn_only_migration.md)。
