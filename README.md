# EngiAgent

EngiAgent is an early MVP for a small, transparent engineering AI agent. The
original demo demonstrates deterministic tool calling and multi-turn conversation.
The engineering mode provides a Chinese CLI for teaching and Chinese-code RC
beam design/evaluation, with three DeepSeek roles and validated Python tools.

## 可视化工作台（2026-10-26）

```powershell
conda activate engiagent
python -m pip install -e ".[ui]"
python -m streamlit run streamlit_app.py --server.port 8511
```

打开 http://127.0.0.1:8511 。提供参数确认、真实计算、二维梁示意、LaTeX规范复核、Agent调用记录、工程DAG和修订比较；对照实验页明确为未执行。

[网页使用说明](docs/ui_quickstart.md) · [界面设计与字段映射](docs/ui_design_spec.md) · [实际验收记录与截图](docs/ui_acceptance.md)

## 中国规范版快速开始（2026-10-25）

```powershell
conda activate engiagent
python run.py --engineering --offline --request examples/engineering/cn_design.json
```

检查参数表，输入“确认”开始。已接入中国规范材料、荷载组合、受弯、受剪、适用构造、裂缝与长期挠度；支持按需DAG、当前进程局部重算和有限改设。

- [运行说明：真实自然语言、已有梁验算、修改和改设](docs/cn_quickstart.md)
- [规范任务与工具映射](docs/rc_beam_cn_design_spec.md)
- [独立算术基准](docs/cn_reference_case.md)
- [实际交付与验证记录](docs/cn_delivery_validation.md)

分项结论限定于支持范围；节点详图、现场构造及完整工程审查仍需工程师完成。

## Current capabilities

- DeepSeek `deepseek-chat`
- A two-node LangGraph ReAct loop
- Tool calling with a deterministic calculator
- Local demo-knowledge lookup
- Thread-level short-term memory
- Observable tool traces in a CLI

Engineering mode includes editable input confirmation and Markdown/JSON reports.
The `cn-2024` mode additionally implements code-based cracked/long-term stiffness,
selective recomputation and bounded redesign. Full engineering compliance,
databases and OCR remain outside the supported scope. A local Streamlit workbench
is available through the optional `ui` dependencies.

## RC 梁教学引擎

当前工作区：`E:/code/Engiagent`。保留原有 `python run.py` Demo。
本节介绍原教学模式，其中国规范核验为“未完成”；中国规范新模式见上方入口。
详见 [工具公式、来源和限制](docs/engineering_tools.md) 与
[阶段验收和操作说明](docs/engineering_acceptance.md)。

```powershell
# 安装（已有环境可直接使用；测试需要 dev 依赖）
D:/anaconda/envs/engiagent/python.exe -m pip install -e ".[dev]"

# 离线示例：显示参数与假设，输入“确认”后计算
D:/anaconda/envs/engiagent/python.exe run.py --engineering --request examples/engineering/paper_normal.json --offline

# 可复现批量运行：--approve 显式确认文件参数与展示的教学假设
D:/anaconda/envs/engiagent/python.exe run.py --engineering --request examples/engineering/paper_normal.json --offline --approve

# 既有梁仅验抗弯（该例计入自重后应失败，退出码 2）
D:/anaconda/envs/engiagent/python.exe run.py --engineering --request examples/engineering/flexure_only.json --offline --approve

# 真实模型：不加 --offline；--query 使用真实 Dispatcher 提取中文任务
D:/anaconda/envs/engiagent/python.exe run.py --engineering --query "请设计简支矩形梁，跨度6m……"

# 离线测试；少量付费真实模型验证另外运行
D:/anaconda/envs/engiagent/python.exe -m pytest -q
D:/anaconda/envs/engiagent/python.exe examples/smoke_engineering.py
```

当前工作区已将 pytest 8.4.2 安装到 `.testdeps/`，可直接运行
`D:/anaconda/envs/engiagent/python.exe scripts/run_tests.py`；原教学基线有74项回归测试，
新增中国规范测试和真实DeepSeek结果见上方交付验证记录。

确认表使用中文名称、分类、原输入/提取值、公制计算采用值、来源和确认状态；
缺失项与由设计工具确定的项目分开显示。可直接输入 `修改 梁高 600 mm`、
`修改 跨度 6 m` 或 `修改 4 6 m`（按表中编号）更正；有量纲的数值必须写单位。
旧的 `span_mm={"value":7.62,"unit":"m"}` 写法仍兼容。支持单位详见工具文档；未知字段、
量纲错误、缺失关键参数均不能确认。输入 `quit` 取消。
`--offline` 只接受结构化文件并使用固定测试角色，不伪装自然语言识别。
结构化文件省略 Dispatcher 模型调用；Design/Evaluation 在非离线模式仍调用 DeepSeek。

结果写入 `outputs/`（默认不加入版本控制），使用唯一文件名，不覆盖旧报告。
JSON 包含原始值、公制值、来源、确认状态、公式版本、输入哈希与完整工具结果。
计算时立即显示设计/验算各阶段的进度与关键结果，最终终端显示简洁方案和验算对比表。
Markdown先给结论、方案、验算对比，再给中文参数、系数和逐步计算结果；技术追溯信息折叠在末尾。
普通数值适度取整，原始输入保留必要精度，判定及JSON中的计算数据始终保留完整精度。
进度以结构化 `ProgressEvent` 写入JSON，也可通过 `run_engineering(..., on_event=callback)` 订阅。
退出码：所请求项目试算通过为 0；试算失败、不完整或执行错误为 2。

纸面参考梁为 25ft、12×20in、4.35ksi、60ksi、0.82/1.00kip/ft。
`paper_normal.json` 计入自重；`paper_ignore_self_weight.json` 明确忽略自重作对照；
`unsized_design.json` 演示初选后不可行时停止；`unsized_feasible.json` 提供较小活载的可行初选。
钢筋公称面积和直径单独保存。
首轮箍筋全跨均布，不输出论文中的分区箍筋总数。

快速体验新版可读输出（整数公制，无需付费模型调用）：

```powershell
D:/anaconda/envs/engiagent/python.exe run.py --engineering --request examples/engineering/metric_design.json --offline
D:/anaconda/envs/engiagent/python.exe run.py --engineering --request examples/engineering/metric_existing.json --offline
```

这两个例子对应6m、300×550mm的梁；设计结果为3根直径20mm纵筋、双肢直径8mm箍筋@250mm。
自然语言真实模型仍使用原来的 `--query` 入口，确认表、进度和报告共用同一展示层。

## Documentation

- [EngiAgent architecture](docs/architecture.md)
- [StructureClaw design notes](docs/structureclaw_notes.md)

## Architecture

```text
START -> Agent -> tool calls? -- no --> END
                   |
                  yes
                   v
                ToolNode
                   |
                   +-----------> Agent
```

The LLM understands and explains. Python tools perform deterministic work.

## Installation

This workspace uses the existing Conda environment at
`D:/anaconda/envs/engiagent/python.exe` (Python 3.11). From the project root:

```powershell
D:/anaconda/envs/engiagent/python.exe -m pip install -e ".[dev]"
```

Copy `.env.example` values into the local `.env` and replace the placeholder:

```dotenv
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-chat
```

The real `.env` is ignored by Git.

## Run

```powershell
D:/anaconda/envs/engiagent/python.exe run.py
```

Type `exit` or `quit` to leave the CLI. Tool calls and tool results are printed
before the assistant's final answer.

Example prompt:

```text
计算 12.5 × 8，同时告诉我 demo 规范中的安全系数。
```

## Tests

```powershell
D:/anaconda/envs/engiagent/python.exe -m pytest
```

The automated suite does not require a DeepSeek API key. A separate smoke test
can exercise the hosted model when `DEEPSEEK_API_KEY` is configured.

```powershell
D:/anaconda/envs/engiagent/python.exe examples/smoke_test.py
```

## Project layout

```text
run.py                         CLI entry point
src/engi_agent/agent.py        LangGraph, tools, model, and memory
src/engi_agent/config.py       Environment configuration
src/engi_agent/tools/          Deterministic tools
src/engi_agent/prompts/        System prompt
knowledge/demo_knowledge.md    Local demo knowledge
examples/basic_demo.py         One-turn usage example
tests/                         Offline unit and graph tests
```

## Roadmap

1. Generic ReAct Agent
2. Engineering knowledge retrieval
3. Engineering calculation tools
4. Engineering workflow
5. Verification and reflection
6. Engineering report generation

## API note

Some older LangGraph tutorials use `MemorySaver` or hand-written tool dispatch.
This MVP uses the current `InMemorySaver`, prebuilt `ToolNode`, and
`tools_condition`. The explicit `StateGraph` is retained so the Agent → Tool →
Agent loop remains visible.
