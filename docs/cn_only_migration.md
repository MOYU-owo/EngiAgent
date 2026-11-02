# CN 单体系迁移与验证

验证日期：2026-11-02。

当前运行代码仅使用中国规范 RC 梁引擎。旧教学工具、独立教学输出契约、通用 ReAct Agent、计算器及演示知识检索入口已从工作区移除。旧教学任务案例不再作为运行输入。

`TaskRequest.code` 仅接受 `cn-2024`，省略时默认 CN。公共工作流、CLI、网页工作台均使用 `CNProfile` 和 `cn_tools.REGISTRY`，不再按规范代码选择两套计算引擎。旧 `--engineering` 兼容开关已移除，直接运行 `python run.py --request ...`。

旧教学参数、目标、单位及其他规范代码会被拒绝。唯一工作流 `cn_workflow.py` 中的 `prepare`、`confirm` 和 `run_engineering` 校验请求及 CN 配置；通过 `model_copy` 修改版本或荷载系数后，即使重新生成确认哈希，也不能开始计算。超出支持范围的任务不能确认。

已逐个删除 `workflow.py`、`schema.py`、`presentation.py` 和 `reporting.py`。所需逻辑分别合并到 `cn_workflow.py`、`cn_schema.py` 和 `cn_presentation.py`，所有源码、示例和测试直接引用 CN 模块，不保留旧模块兼容层。机制实验的源文件哈希追溯同步使用现存 CN 文件。

离线角色、程序角色和 DeepSeek 角色使用同一个 CN 内核，仅模型调用环节不同。咨询、工具 DAG、缓存、参数修订及有限改设继续保留。

## 本次验证

使用 `.vscode/settings.json` 指定的 `D:/anaconda/envs/engiagent/python.exe`，未安装或变更环境依赖。

| 检查 | 结果 |
| --- | --- |
| `python scripts/run_tests.py` | 157 passed；包括 CN 算术基准、非 CN 输入拒绝、配置篡改阻断、报告、咨询及 Streamlit 交互；工作流合并后去掉了一次重复入口测试 |
| `python examples/cn_workflow_demo.py` | 新设计、已有梁、局部抗弯、有限改设、梁高修订通过；无解案例按预期失败；局部重算与完整重算输出相同 |
| `python examples/run_mechanism_experiment.py` | 20 个案例，每组 60 次运行；DAG 与 DAG+缓存均与完整重算结果一致 |
| `python run.py --offline --approve --request examples/engineering/cn_design.json --output-dir outputs/cn_only_validation` | 退出码 0，五项检查通过，Markdown 和 JSON 报告成功生成 |
| 运行源代码引用扫描 | 无旧 Agent、教学工具、教学输出契约及教学目标的残留引用 |
| `git diff --check` | 通过 |

示例验收结果保存于 `outputs/cn_validation/`，机制实验保存于 `outputs/research/`，命令行报告保存于 `outputs/cn_only_validation/`。这些运行产物由 Git 忽略。

本次没有调用真实 DeepSeek 服务；模型接口通过离线脚本模型验证。运行验证说明已实现功能在上述测试中符合预期，不代表已覆盖完整工程审查。当前适用范围以[设计规格](rc_beam_cn_design_spec.md)及实际报告为准。

原论文、初始架构和早期评审作为研究历史保留，其中的非 CN 描述不参与运行。继续清理了无调用的字段检查、展示函数、实验记录占位类及未使用导入；正式实验协议说明仍保留。
