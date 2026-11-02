# EngiAgent

EngiAgent 是仅运行中国规范的钢筋混凝土梁设计、验算与咨询原型。2026-11-02 起移除了旧教学计算分支和通用 Agent Demo；所有入口默认 `cn-2024`，其他规范代码会被拒绝。

## 启动工作台

```powershell
conda activate engiagent
python -m pip install -e ".[dev,ui]"
python -m streamlit run streamlit_app.py --server.port 8512 --server.address 127.0.0.1
```

打开 <http://127.0.0.1:8512>。加载案例，检查参数并确认后运行。工作台提供设计、规范复核、工具 DAG、修订比较、专家咨询和可执行机制对照实验。

执行模式包括离线确定性角色、真实 DeepSeek 角色、以及“DeepSeek · 仅需求与咨询”。这三种模式均使用同一套 CN 参数、公式和工具；区别是哪些环节调用模型。

## 命令行

```powershell
# 显示参数表，输入“确认”后计算
python run.py --offline --request examples/engineering/cn_design.json

# 已有梁独立验算；可在同一进程修改并重新确认
python run.py --offline --request examples/engineering/cn_existing.json --session

# 仅抗弯、有限改设、达到上限停止
python run.py --offline --request examples/engineering/cn_flexure_only.json
python run.py --offline --request examples/engineering/cn_redesign.json
python run.py --offline --request examples/engineering/cn_no_solution.json

# 批量运行：显式确认文件参数和规范假设
python run.py --offline --approve --request examples/engineering/cn_design.json

# 真实模型提取本次需求，合并显式模板后仍需确认
python run.py --base-request examples/engineering/cn_design.json --query "新设计简支矩形梁，跨度6m，其余采用指定模板。"
```

`--code` 仅接受 `cn-2024`。任务文件省略 `code` 时同样使用 CN；旧教学字段、目标、配置及显式其他规范任务不能转入计算。

参数表可输入 `修改 梁高 600 mm`、`修改 混凝土等级 C40`；修改后必须重新确认。报告以唯一文件名保存至 `outputs/`，包含完整精度 JSON、中文 Markdown、依据、公式版本、缓存记录和修订历史。退出码：请求检查通过为 0，失败、不完整或执行错误为 2。

## 支持范围和依据

- 简支矩形 RC 梁，全跨均布恒活载，单层受拉筋；已有梁可只检查指定项目。
- 材料、作用组合、受弯、受剪、适用构造、裂缝及长期挠度。
- GB/T 50010-2010（2024修订及未修订条文）、GB 55001-2021、GB 55008-2021、GB 50009-2012 的已实现子集。
- 按目标执行 DAG、按输入和版本复用缓存、有限轮次自动改设。
- 咨询解释实际工具证据；明确的自然语言参数修改先生成建议，采用、确认后才重算。

当前边界为普通房屋、50 年、二级安全、一类环境及已列明的结构条件。请求分项通过仅说明支持范围内的检查结果，完整节点、施工、抗震及工程整体审查仍未覆盖。暂未实现 OCR、跨进程恢复、跨任务学习与多候选最优搜索。

## 模型配置

离线运行不需要密钥。使用真实 DeepSeek 时，将 `.env.example` 的配置写入本机 `.env`：

```dotenv
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-chat
```

`.env`、运行输出和本机环境不加入版本管理。

## 验证与资料

```powershell
python scripts/run_tests.py
python examples/cn_workflow_demo.py
python examples/run_mechanism_experiment.py
# 以下两个脚本会调用真实模型
python examples/smoke_cn_engineering.py
python examples/smoke_consultation.py
```

[CN 单体系迁移与验证](docs/cn_only_migration.md) · [当前架构](docs/architecture.md) · [CLI 操作](docs/cn_quickstart.md) · [工作台操作](docs/ui_quickstart.md) · [公式与适用范围](docs/rc_beam_cn_design_spec.md) · [独立算术基准](docs/cn_reference_case.md) · [咨询与机制实验说明](docs/consultation_delivery.md)

原文献、初始设计和早期评审文档保留为研究历史；涉及旧教学分支和 Demo 的描述不代表当前可运行功能。
