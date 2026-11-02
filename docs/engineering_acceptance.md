# 工程入口操作与验收：仅 CN

更新：2026-11-02。旧教学模式和通用 Demo 已移除，原入口说明不再适用。

```powershell
python run.py --offline --request examples/engineering/cn_design.json
```

核对参数表后输入“确认”。可先用 `修改 梁高 600 mm` 等命令修改；缺项或无效值必须修正。省略规范代码时使用 CN；旧规范代码和参数不会退回其他计算模式。

完整操作见 [CN 快速开始](cn_quickstart.md)，本次验证见 [CN 单体系迁移记录](cn_only_migration.md)。

离线验收命令：

```powershell
python scripts/run_tests.py
python examples/cn_workflow_demo.py
python examples/run_mechanism_experiment.py
```

验证覆盖参数确认、规范与字段拒绝、CN 独立算术、五项验算、局部重算、有限改设、失败阻断、模型异常、报告精度、专家咨询与工作台交互。真实模型验证独立运行，结果与离线测试分别记录。
