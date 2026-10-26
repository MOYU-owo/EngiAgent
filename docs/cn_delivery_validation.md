# 中国规范版实际交付与验证记录

本文保留2026-10-25核心引擎交付时的快照。2026-10-26新增的Streamlit工作台见 [UI验收记录](ui_acceptance.md)。

日期：2026-10-25。范围按照用户确认的 `rc_beam_cn_implementation_plan.md`：以简单实现跑通规范计算、动态依赖、局部重算和有限改设；界面、跨进程恢复与正式批量实验暂缓。

## 交付对照

|计划阶段|实际完成|证据|
|---|---|---|
|规范及任务基线|相关页定位、2015正文+2024修订关系、GB55008补齐、工具映射、公式核对、独立算例|rc_beam_cn_design_spec.md、rc_beam_cn_formula_review.md、cn_reference_case.md|
|中国规范计算|C25—C50材料、HRB400/500纵筋、普通箍筋；荷载组合、受弯、受剪、适用构造、裂缝及长期挠度|cn_tools.py；完整设计和已有梁报告；算术及边界测试|
|按需DAG与缓存|明确工具输入字段及依赖；按目标求闭包与拓扑顺序；公式/规范/输入哈希；按阶段隔离缓存|dependency_graph.py、cn_workflow.py；直接弯矩及梁高修改测试|
|局部重算|同一进程修改、重新确认、历史保留；另计与已含自重分别传播失效|--session；新旧状态JSON；局部与全量输出逐项一致测试|
|有限改设|LangGraph外层循环，单轮内部DAG；固定截面下增加同直径配筋；未固定梁高仅在明确上限内可增大|两轮通过、三轮停止案例；每轮理由、候选、工具结果保留|
|可演示交付|中文参数表、进度结果、分项过程与修订表；自然语言及显式模板；Markdown/JSON；实验记录模板|cn_quickstart.md、cn_experiment_protocol.md及示例脚本|

## 程序结构

```text
自然语言 / JSON / 显式模板
  → Dispatcher (DeepSeek structured output)
  → TaskRequest.code=cn-2024 → 类型/单位标准化 → 人工确认及哈希
  → LangGraph：Design → Evaluation → 条件判断 → 有限改设 → Design
       每阶段：依赖闭包 → 输入/版本比较 → 执行或复用 → 输出模型校验
  → 当前方案、历史修订、中文报告与完整JSON
```

|文件|职责|
|---|---|
|src/engi_agent/engineering/cn_schema.py|中国规范参数类型、支持边界、必需输入和固定配置|
|src/engi_agent/engineering/cn_tools.py|白名单确定性计算、材料参数与工程判定|
|src/engi_agent/engineering/cn_outputs.py|工具输出必需数值及判定结构校验|
|src/engi_agent/engineering/dependency_graph.py|工具直接输入、版本、条件依赖与拓扑计划|
|src/engi_agent/engineering/cn_workflow.py|确认、失效与复用、独立验算、方案修订及有界循环|
|src/engi_agent/engineering/cn_presentation.py|中文参数与结果、规划轨迹、修订原因、依据与限制|
|原workflow.py/cli.py/reporting.py|保留教学入口，按code路由新模式|

模型只提取参数和返回被约束的工具计划；Python规划器决定依赖，Python工具给出数值结论。没有让模型执行任意代码。Evaluation使用实际配筋重新计算，不能复用Design的通过结论；缓存键按阶段隔离。

## 实际验证

项目环境：D:/anaconda/envs/engiagent/python.exe。未为本轮新增第三方依赖。

### 离线回归

执行：`python scripts/run_tests.py`。

实际结果：**110 passed in 4.10s**。含原有74项回归与新增36项参数化测试。测试日志：outputs/cn_validation/pytest.txt。

覆盖：独立算术及单位边界、缺项与未给截面、材料底线、承载不足、净距、锚固、裂缝与挠度超限、零荷载、模型格式/API异常替身、工具异常与输出缺失、真正依赖阻断、版本失效、自重条件依赖、局部/全量一致、进程内交互、自然语言模板合并、序列化和报告、有限改设及达到上限停止。

新增测试中使用的模型替身均为离线测试，不作为真实DeepSeek证据。

### 六个实际演示场景

执行：`python examples/cn_workflow_demo.py`。

|报告（outputs/cn_validation下）|实际结果|
|---|---|
|cn_design.md|3Φ20，跨内双肢Φ8@350，锚固区@100，五项检查通过|
|cn_existing.md|保留已有3Φ20及@250，仅执行Evaluation，五项通过|
|cn_flexure_only.md|100kN·m直接设计弯矩，只运行材料、几何、内力来源及抗弯；通过|
|cn_redesign.md|初始L/600挠度不通过，3Φ20→4Φ20，两轮通过|
|cn_no_solution.md|裂缝限值0.01mm，确认的固定尺寸和三轮范围内未通过；正确停止|
|cn_height_revision.md|梁高550→600mm；复用材料，另计自重链及相关验算重算；与全量计算逐项一致|

完整汇总为 outputs/cn_validation/summary.json。报告由真实工具结果生成，不是预写预期文字。

### 真实DeepSeek

执行：`python examples/smoke_cn_engineering.py`，使用现有.env的deepseek-chat配置；不记录密钥。

已实际通过：完整中文自然语言需求 → Dispatcher全部参数与受控参考案例匹配 → Design → Evaluation → 请求项目通过；另一次已有梁仅抗弯由真实Evaluation完成并通过。

本次成功运行报告：

- outputs/cn_live/beam_f1f515c0382f.md（完整自然语言设计）
- outputs/cn_live/beam_23923d6e99b0.md（已有梁仅抗弯）

成功前两次提取校验在“安全等级二级”标准化处停止，没有进入计算、没有产生通过结论。已增加明确提示和“二级→2”的确定性标准化，并加入离线回归。成功调用记录属于当时工程版本；此后增加的输出契约、报告、模板和边界处理另由当前离线测试与演示复核，不冒充再次真实API执行。

## 使用入口

推荐从 [快速使用说明](cn_quickstart.md) 开始：

```powershell
python run.py --engineering --offline --request examples/engineering/cn_design.json
python run.py --engineering --offline --request examples/engineering/cn_existing.json --session
python run.py --engineering --base-request examples/engineering/cn_design.json --query "按中国规范新设计一根梁，跨度6m，其余采用指定模板。"
```

## 保留的边界与后续事项

此版是限定构件的中国规范计算原型。端部采用明确的充分受拉直锚保守方案，例子使用宽支座；一般短伸入、弯锚和复杂节点未展开。理想铰支不等同于实际部分约束支座。首箍、封闭箍、拉结、防火及完整耐久审查需要详图和工程师落实。

`evaluation.status=pass`表示本次请求的实现项目通过；`overall_status=incomplete`保留完整工程审查尚未完成的事实。仅抗弯不推导其他检查通过。

当前无Streamlit、OCR自动化、跨进程任务恢复或正式人工/通用模型批量实验；这些是已明确暂缓的后续路线。原教学模式、原Demo及其回归保持可用。
