# EngiAgent 可视化工作台设计说明

设计始于2026-10-25，验收于2026-10-26。先审查内核及六类实际演示，再定义UI；此文描述实现约定，不把界面图当作执行证据。

## 1. 现状审查与边界

已检查CN Schema、Tools、Outputs、dependency_graph、cn_workflow、确认/报告/修订模块，及cn_quickstart、cn_delivery_validation、cn_reference_case、cn_experiment_protocol。读取五份案例请求与六份outputs/cn_validation/cn_*.json结果，包括各轮tools和trace。第六类梁高修改没有独立请求文件：以cn_existing为基准调用revise，将550改600，原JSON保存两次修订。

可复用接口：`prepare(TaskRequest)`校验及列缺项，`confirm(EngineeringState)`确认并盖输入哈希，`run_engineering(state, roles, on_event)`实际运行，`revise(state, changes, targets=...)`创建未确认修订，`markdown_report(state)`生成报告。UI不调用CLI、不更改规范公式或DAG行为。

现有记录限制：role_events仅有角色/状态/工具列表，不含完整模型调用输入输出、时间或内部思维；ProgressEvent在CN工具完成时发出，未记录每个工具起始时间；ToolResult未记录耗时或token；跳过的工具不出现在tool_results。UI不编造这些字段。

## 2. 参考与视觉系统

实际读取的公开页面：

- [Calcs功能页](https://calcs.com/features)：采用“输入—计算值—公式—条文—报告”同页追溯模式；不照搬其商业宣传及全面合规宣称。
- [SimScale平台文档](https://www.simscale.com/docs/platform/)：工作区导航、参数设置、中央工程视图及状态区分工；按任务只显示相关设置。
- [LangSmith Studio文档](https://docs.langchain.com/oss/python/langgraph/studio)：图与逐事件输入/输出检查器并列；展示结构化计划及工具结果，不显示虚构思维链。
- [Carbon首页](https://carbondesignsystem.com/)和[现行数据表格指南](https://www.carbondesignsystem.com/building-blocks/core/components/data-table/guidelines)：清晰层级、紧凑表格、可展开详情、显式状态。旧`guidelines/typography/overview/`地址不可访问，未声称看过该字体页面。

上述为公开文档与功能页研究，未登录或操作其付费工作区。

浅色主题：背景#F3F5F8，面板#FFFFFF，主色#173E73，文字#172B43，辅助文字#607087，边线#DCE3EC。通过用绿、失败用红、待确认用琥珀、复用用蓝、未执行用灰，始终附文字，不仅依靠颜色。无渐变、装饰统计和无意义动画。

使用系统中文无衬线字体；标题24–28px、分区18–20px、正文14–16px，数据等宽数字；4/8px间距体系，面板内距16–24px。桌面1366–1920px优先，内容最大约1800px。表格保留单位独立列，数值右对齐，显示取整与判定精度分离。公式使用Streamlit LaTeX/KaTeX，仅转写已实现公式，不在UI计算规范结果。

## 3. 页面信息架构与线框

共用左侧窄导航：设计工作台 / 计算与规范复核 / Agent与动态规划 / 对照实验。底部显示科研教学原型及会话存储范围。顶栏为案例名、cn配置版本、修订、UI阶段和执行模式。

### A 设计工作台

```text
[EngiAgent]  案例 / 规范配置 / 修订 / 待确认或执行状态
┌需求与参数（约38%）────────┬工程工作区（约62%）─────────┐
│模板/JSON上传/自然语言提取 │跨度、截面、配筋、状态摘要   │
│新设计/已有梁 + 目标       │简支梁立面 + 按比例截面SVG  │
│几何|材料|荷载|配筋|构造   │实际作用和支座；缺数据不补画 │
│值和单位编辑              │五项复核表 / 运行进度       │
│原值/规范化值/来源/确认详情│查看完整结果 / 下载MD、JSON │
│校验 → 确认 → 运行        │历史结果与当前草稿明确分开   │
└───────────────────────┴─────────────────────────┘
```

自然语言仅显式按钮触发DeepSeek，可选显式模板合并；离线模式不伪装自然语言解析。参数编辑即撤销UI确认与运行资格，必须先校验再确认；缺项或非法值阻止运行。开启改设及轮次上限也纳入确认。已有梁不允许自动改设。

加载模板不运行、不调用模型。切换模式后实际配筋或荷载等缺项由同一prepare接口列出。模板“梁高修改演示”对应已有梁基准，先执行，再由工程师改成600mm并确认；不隐藏执行基准或伪造缓存。

### B 计算与规范复核

```text
请求完成状态 | 工具执行情况 | 完整工程审查=未完成
受弯 / 受剪 / 构造 / 裂缝 / 长期挠度
  实际值—需求/承载/限值—单位—结论及失败原因
  LaTeX公式（按工具及条件分支选择）
  该工具实际输入、上游材料及几何、输出数值、假定
  ToolResult.code_refs / formula_version / inputs_hash
  原始ToolResult JSON与诊断（展开）
```

无结果、未请求、上游阻断、函数异常、模型范围失败、数值检查失败分别显示。所有数字投影自实际输出，不以界面公式重复计算。下载复用内核报告；下载按钮、展开和页面切换不发LLM请求。

### C Agent与动态规划

Agent图与工程DAG为两个视图，不合并为一张“智能图”。

```text
[Agent视图] 实际角色调用顺序/反馈 → 事件选择 → 实际输入输出
[DAG视图] 修订选择 + Design/Evaluation阶段
           本轮实际子图 → 节点选择器 → 输入/输出/版本/执行与复用原因
[修订比较] 两轮选择 → 参数/方案变化 → 重算及复用节点 → 检查结论
```

DAG边取ToolResult.inputs.upstream中真实前置工具；未运行时仅展示build_plan计划，标“待执行”。默认只显示当前子图；其他预定义工具作为“本阶段未计划”列表，绝不当作已执行。执行完成与检查不通过可同时存在。Graphviz无原生点击回传，因此用紧邻图的节点选择器选择检查对象，不伪装图中点击功能。

方案数据从revisions读取，输入修改前后、candidate、evaluation、tools及trace均使用对应轮次快照。旧结果缺少Agent调用输入时明确“历史记录未保存”；不反推为当时的模型输入。

### D 对照实验

显示“正式对照实验未执行”。只定义ExperimentRecord接口：案例ID、执行组、规范版本、输入/输出证据、可选耗时/token/费用及复核结论。无真实记录时不显示数值统计或准确率图。链接现有实验协议。

## 4. 状态与操作流程

`empty → editing → validated → confirmed → running → completed`。

解析使用`parsing`，异常使用`error`；缺项保持editing并显示missing_parameters。参数或配置改变立即dirty，confirmed失效；旧result可在复核页查看，明确为历史快照，不能显示成当前草稿已通过。只有confirmed状态可运行；完成后重复刷新不再次运行。新任务加载清除旧任务状态；修改现任务保留真实cache/history。

完整流程：选择/上传/提取 → 编辑 → 校验 → 查看确认表及边界 → 确认 → 显式运行 → 浏览结果与追踪 → 修改 → 再次校验和确认 → 局部重算。

## 5. 字段映射

|组件|实际字段/接口|限制|
|---|---|---|
|顶栏|request.code、profile.version、design_revision、适配层UI阶段|UI阶段不是工程判定|
|参数确认|request.parameters的value/unit/raw_value/raw_unit/source/confirmed；missing_parameters|原值与采用值分别列出|
|梁示意|parameters、candidate、section_geometry和load_combination输出|缺尺寸/配筋不猜测；图是示意非施工图|
|验算表|evaluation.checks及evaluation.*工具outputs|无工具有效输出则不显示“通过”|
|请求状态|evaluation.status|与ToolResult.status分开|
|工程审查|evaluation.overall_status、code_status、unimplemented|原型overall_status保持incomplete|
|公式/依据|cn_tools已实现分支的只读LaTeX转写、ToolResult.inputs/outputs/code_refs/formula_version|前端不计算判定|
|DAG|inputs.upstream；plan_trace.action/reason；ToolResult.status|缺trace时标“未记录”，不猜是否复用|
|Agent图|role_events、progress_events；适配层新记的真实RoleClient调用|无内部思维、token、未记录耗时|
|修订|revisions[*].parameters/candidate/evaluation/tools/trace/reason|按快照而非当前根输入回填|
|报告|markdown_report(state)、state.model_dump_json()|内存下载，不触发执行|

## 6. 最小适配层与依赖

新增`engi_agent.ui.service.WorkbenchSession`负责会话阶段、显式操作、保留cache及历史；`RecordingRoles`包装现有RoleClient，实际调用前后记录输入、结构化输出、成功/失败和真实时间。独立保存UI审计数据，不改变EngineeringState的工程语义，不记录密钥或原始provider异常。

`projections.py`投影表格、DAG、修订比较；`formulas.py`存只读LaTeX表示；`diagrams.py`生成真实数据SVG和DOT；`app.py`仅渲染及触发显式操作。根`streamlit_app.py`作为启动入口。Streamlit/Graphviz列为ui可选依赖；不引入React、数据库、额外HTTP后端或云追踪服务。

进度回调只显示核心实际事件，核心没有工具开始时间，UI不生成工具耗时。会话状态在Streamlit连接内存中，不能宣传为跨进程恢复；服务重启或连接丢失可能丢失任务。

## 7. 验收策略

服务层实际运行六类案例，与原JSON/Markdown逐值对照；测试缺项、非法数值、模型与工具错误、修改未确认、重复运行保护与缓存一致性。Streamlit AppTest检查实际页面、加载/确认/执行/修改、导航与下载不重复调用模型。浏览器可用时在1366与1920桌面检查布局、LaTeX、图与状态，保存截图；最后执行所有原回归测试。测试与截图结果另记`ui_acceptance.md`。
