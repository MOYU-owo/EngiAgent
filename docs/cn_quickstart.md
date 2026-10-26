# 中国规范版：直接运行

本文为CLI操作说明。网页入口见 [可视化工作台使用说明](ui_quickstart.md)。

本轮新增功能：按中国规范计算RC简支梁、已有梁独立验算、裂缝与长期挠度、按目标选择工具、当前进程内修改参数并局部重算、有限改设。原教学版与Demo仍可使用。

## 1. 先跑一个完整案例

在PowerShell进入项目并启用已有环境：

```powershell
cd E:\code\Engiagent
conda activate engiagent
python run.py --engineering --offline --request examples/engineering/cn_design.json
```

屏幕首先显示参数确认表。输入 **确认** 后开始；也可以先输入 `修改 梁高 600 mm` 再确认。

基准参数为6m跨度、300×550mm、C30、HRB400、恒载10和活载5kN/m，恒载另计梁自重。活载系数和全部构造假定见确认表。支座宽1000mm是为演示800mm充分受拉直锚而选择的宽支座，不应照搬为实际节点尺寸。

预期方案：**下部3Φ20，跨内双肢Φ8@350，锚固区@100**。抗弯、抗剪、适用构造、裂缝和长期挠度均通过；裂缝约0.173mm，长期挠度约11.714mm。程序最后打印中文Markdown报告和JSON路径。

`--offline`使用确定性测试角色，不会调用大模型；去掉它就使用现有`.env`配置中的真实DeepSeek角色。

## 2. 真实大模型 + 简短自然语言

使用显式案例模板，可以避免每次重新输入材料和全部构造条件。模型仅提取这次自然语言中的值，程序合并模板后展示全部参数，仍需你确认。

```powershell
python run.py --engineering --base-request examples/engineering/cn_design.json --query "按中国规范新设计一根梁，跨度6m，梁宽300mm，梁高550mm，恒载10kN/m不含自重，活载5kN/m，其余采用指定模板。"
```

确认表中的“显式案例模板”是你选择的模板参数，“模型提取”是本次自然语言提取值。这里不从自然语言猜测缺少的工程条件。也可以不提供模板，输入完整需求；完整自然语言范例见 `examples/smoke_cn_engineering.py` 中的QUERY。

若只想测试真实Design和Evaluation角色、直接使用参数文件：

```powershell
python run.py --engineering --request examples/engineering/cn_design.json
```

## 3. 已有梁独立验算

```powershell
python run.py --engineering --offline --request examples/engineering/cn_existing.json
```

该文件已给出300×550mm、下部3Φ20及跨内双肢Φ8@250，程序只执行Evaluation，不生成新设计。实际工程请先编辑文件或在确认表更正输入。

仅抗弯示例已直接给出100kN·m设计弯矩，省略荷载组合、受剪、裂缝和挠度：

```powershell
python run.py --engineering --offline --request examples/engineering/cn_flexure_only.json
```

真实模型解析局部验算可用：

```powershell
python run.py --engineering --base-request examples/engineering/cn_existing.json --query "按中国规范验算已有梁，只检查抗弯，设计弯矩100kN·m，下部3根直径20mm钢筋，其余采用指定模板。"
```

## 4. 同一进程修改与局部重算

```powershell
python run.py --engineering --offline --request examples/engineering/cn_existing.json --session
```

先输入 `确认`；得到报告后输入 `修改 梁高 600 mm`，检查新表格并再次 `确认`。输入 `quit` 结束。

材料等未变化的结果会复用；另计自重时，梁高变化会触发自重、内力及相关验算重算。若恒载已经包含自重，则截面变化不会自行改变该恒载。每次修订均有独立报告；报告的“规划与复用记录”解释执行与复用原因。

本入口支持中文参数修改命令；跨进程重新打开旧任务的恢复功能留待后续。

## 5. 有限改设

```powershell
python run.py --engineering --offline --request examples/engineering/cn_redesign.json
```

这个案例把挠度限值收紧到L/600。预期首轮3Φ20挠度不通过，第二轮4Φ20通过，固定的截面尺寸不变。最多3轮，历史方案写入报告及JSON。

`cn_no_solution.json`把裂缝限值收紧至0.01mm，用于验证停止行为：达到轮次上限后报告不通过，不会无限循环。此处“未找到方案”指确认的候选范围及轮次内，不是数学上证明所有设计均无解。

任一中国规范新设计可以用 `--auto-redesign --max-iterations 3` 显式开启改设；已有梁验算不允许自动改变原方案。

## 6. 一次验证全部场景

```powershell
python examples/cn_workflow_demo.py
python scripts/run_tests.py
```

演示报告保存在 `outputs/cn_validation/`，包括 `cn_design.md`、`cn_existing.md`、`cn_flexure_only.md`、`cn_redesign.md`、`cn_no_solution.md` 和 `cn_height_revision.md`。

完整自然语言及真实角色验证（会调用DeepSeek）：

```powershell
python examples/smoke_cn_engineering.py
```

脚本仅在模型提取值与受控参考案例完全匹配时自动确认；否则停止。普通使用由工程师核对确认。

## 如何读结果

- **执行完成**：函数正常返回；看同一行的“验算通过/不通过”及关键数值。
- **请求项目通过**：仅本次请求且已实现的项目通过；仅抗弯不会被解释为全梁设计完成。
- **请求项目不通过**：存在工程检查失败，报告列明原因。
- **执行错误/上游阻断**：模型或工具未产生有效结果，不能判断通过。
- JSON的`evaluation.overall_status`保留`incomplete`，因为支座节点、现场落实及完整工程审查不由本原型覆盖。`evaluation.status`表示本次请求的检查状态。

规范与公式：[任务规范](rc_beam_cn_design_spec.md)、[原文复核](rc_beam_cn_formula_review.md)、[独立基准算例](cn_reference_case.md)。
