# EngiAgent

EngiAgent is an early MVP for a small, transparent engineering AI agent. The
current version is deliberately domain-neutral: it demonstrates how a language
model can decide when to call deterministic tools, observe their results, and
continue a multi-turn conversation.

## Current capabilities

- DeepSeek `deepseek-chat`
- A two-node LangGraph ReAct loop
- Tool calling with a deterministic calculator
- Local demo-knowledge lookup
- Thread-level short-term memory
- Observable tool traces in a CLI

It does not yet implement real engineering analysis, engineering codes, RAG,
databases, a web UI, or report generation.

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
