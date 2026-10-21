# 首轮核心引擎：操作与验收

日期：2026-10-21。工作区 E:/code/Engiagent；Python 3.11.17。
原设计文档中的 D:/code/EngiAgent 与 Python 3.11.16 不代表当前环境。

## 阶段 1：基础、数据模型和确认

- 保留原 Demo、包名与 EngiAgent.run_turn()。
- 新增 TaskRequest / ParameterValue / BeamParameters / TeachingProfile /
  EngineeringState / ToolResult / EvaluationResult，以及每个工具的强类型输出模型。
- 原始参数及单位、公制参数及单位、来源、确认状态分别保存。
- 确认哈希涵盖任务和假设；确认后修改任一项即拒绝计算。
- 命令行可更正字段、补充缺失条件或取消；不实现跨进程恢复。

```powershell
D:/anaconda/envs/engiagent/python.exe run.py --engineering --request examples/engineering/paper_normal.json --offline
```

预期：出现包含全部参数、公式系数、适用范围和未完成事项的确认表。
输入“确认”开始；输入 `quit` 取消。缺失荷载不能确认。
更正示例：`span_mm={"value":7.62,"unit":"m"}`。

## 阶段 2：确定性计算

计算说明先于函数实现写入 [engineering_tools.md](engineering_tools.md)。
每个工具验证输入和输出，保存输入哈希、公式版本、依据、警告与错误。
正常试算计入自重；忽略自重仅作为明确标记的参考对照。
剪力查询位置与设计临界截面分开，不能通过查询跨中剪力绕过抗剪验算。
不实现分区箍筋截断/总数、开裂刚度或长期挠度。

|任务文件|预期行为|
|---|---|
|paper_normal.json|保留304.8×508mm；计入自重，4根参考纵筋，双肢箍筋间距220mm；所实现项目试算通过|
|paper_ignore_self_weight.json|明确忽略自重；3根参考纵筋；报告附假设警告|
|existing_beam.json|已有3根纵筋且计入自重，抗弯失败，仍呈现其他已请求检查|
|flexure_only.json|只执行抗弯及所需布置检查；跳过抗剪和挠度，抗弯失败|
|unsized_design.json|参考荷载下初选300×500mm；离散配筋不满足受拉控制，停止并说明原因|
|unsized_feasible.json|活载明确降低到0.6kip/ft；工具初选截面后可完成教学试算|

```powershell
D:/anaconda/envs/engiagent/python.exe run.py --engineering --request examples/engineering/paper_ignore_self_weight.json --offline --approve
```

`--approve` 是显式批量确认参数与假设；适用于已检查的固定输入。
输入模板中的 Ec=27568.7MPa 与 L/240 是明确的教学输入，不是中国规范默认值。

## 阶段 3：LangGraph 双入口与三个角色

Dispatcher：真实模型提取自然语言，或直接加载显式结构化任务。
Design 子图：模型组织受规则约束的工具计划，依次执行初选、几何、荷载、内力、受弯、受剪。
Evaluation 子图：重新计算实际截面、荷载与内力，再执行目标检查。
既有梁直接进入 Evaluation；设计输出经 Evaluation 校核后结束。
失败即报告，不增大截面、不重试设计，也不宣称是 DAG 局部重算。

LLM 输出只用于结构化提取与受限工具计划，不向最终报告写入模型自造数值或判定。
三个角色是 Dispatcher/Design/Evaluation，不是论文咨询模块内部的 primary/verification/integrator。

## 阶段 4：报告与验证

Markdown 与 JSON 写到 outputs/ 下的唯一文件名，不覆盖旧报告。
报告保存所有输入、候选、完整工具输出、分项结果及未完成项。
status=success 只表示工具执行成功；outputs.pass 表示该项教学检查结果。
evaluation.status 表示所请求项目 pass/fail/incomplete/error；
overall_status 始终 incomplete，中国规范核验始终“未完成”。

离线测试覆盖原 Demo、新设计、独立验算、仅抗弯、缺参、单位和非法值、确认后修改、
自重、实际钢筋几何、独立手算、挠度超限、不可行截面、模型/工具错误及报告。

```powershell
# 标准安装路径
D:/anaconda/envs/engiagent/python.exe -m pip install -e ".[dev]" -c constraints-core.txt
D:/anaconda/envs/engiagent/python.exe -m pytest -q

# 可选：将测试依赖只安装到当前项目，避免修改系统环境
D:/anaconda/envs/engiagent/python.exe -m pip install --target .testdeps pytest==8.4.2
D:/anaconda/envs/engiagent/python.exe scripts/run_tests.py

# 付费真实模型验证，和离线测试分开
D:/anaconda/envs/engiagent/python.exe examples/smoke_engineering.py
```

真实验证脚本先逐字段比较 Dispatcher 提取结果与已检查参考输入，完全一致才确认。
已验证：自然语言新设计中的三个真实角色均成功；已有梁仅抗弯入口由 Evaluation 正确返回 fail。
JSON/Markdown 实际报告见本地 outputs/live/；离线报告见 outputs/offline/。
最终执行记录：

- 项目内隔离安装 pytest 8.4.2；`python scripts/run_tests.py`：**55 passed**。
- 原 Demo 的全部既有测试包含在上述结果中，保持通过。
- 6个结构化参考案例均已运行并生成报告；结果与上表一致。
- 真实 DeepSeek：自然语言设计完成 Dispatcher、Design、Evaluation 共3次角色调用；
  已有梁仅抗弯再调用 Evaluation 1次，正确识别承载力不足。
- 命令行子进程验证 paper_normal/unsized_feasible 返回0，flexure_only返回2；
  UTF-8中文输出正常，Markdown和JSON均落盘。
- `git diff --check` 通过。

当前工作区未向系统 Python 安装测试包；`.testdeps/` 不纳入版本控制。
本机现在可直接运行 `D:/anaconda/envs/engiagent/python.exe scripts/run_tests.py`。

## 仍属后续阶段

中国规范与完整构造、开裂/长期挠度和裂缝、DAG/缓存失效重算、自动改设、SQLite
恢复、Streamlit、OCR、多方案与偏好选择均未实现，不应在汇报中列为已完成能力。

## 工程师可读性更新（2026-10-21）

- 中文参数确认表：分类、原值、公制采用值、来源、确认/缺失/计算状态。
- 更正支持中文或编号，如 `修改 梁高 600 mm`；原JSON编辑语法兼容。
- 设计/验算工具执行前后实时输出进度和关键结果；模型计划等待和失败也有明确反馈。
- 新增ProgressEvent及可选on_event回调，进度记录随状态保存；观察者不能修改计算结果。
- 最终报告改为方案、验算对比、确认表、教学系数、执行流程和分阶段中文计算表。
- 已有梁直接显示实配参数，不再显示空候选对象；未执行、阻断和失败项目不能显示通过。
- 原始完整精度数据继续保存JSON，报告适度取整，技术哈希折叠展示；旧状态可重新生成新版报告。
- 新增metric_design / metric_existing两个整数公制示例。运行方式见README。
- 原有55项测试继续通过；新增参数表/中文编辑、实时进度、错误状态、输出精度、旧状态兼容与命令行展示测试。
- 更新后共74项测试通过；本轮未更改公式和材料模型。
