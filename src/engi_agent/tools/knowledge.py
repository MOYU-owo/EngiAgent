"""Simple local Markdown lookup used in place of a RAG system."""

from pathlib import Path
import re

from langchain.tools import tool


PROJECT_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_PATH = PROJECT_ROOT / "knowledge" / "demo_knowledge.md"


def _sections(markdown: str) -> list[str]:
    chunks = re.split(r"(?=^##\s+)", markdown, flags=re.MULTILINE)
    return [chunk.strip() for chunk in chunks if chunk.strip() and chunk.startswith("##")]


def _query_terms(query: str) -> set[str]:
    lowered = query.lower()
    latin_terms = set(re.findall(r"[a-z0-9_.-]{2,}", lowered))
    chinese_runs = re.findall(r"[\u4e00-\u9fff]+", lowered)
    chinese_bigrams = {
        run[index : index + 2]
        for run in chinese_runs
        for index in range(max(0, len(run) - 1))
    }
    return latin_terms | chinese_bigrams


def search_demo_knowledge(query: str) -> str:
    """Return the most relevant local Markdown sections for a query."""
    query = query.strip()
    if not query:
        return "未提供查询内容。"
    if not KNOWLEDGE_PATH.is_file():
        return f"本地知识文件不存在：{KNOWLEDGE_PATH}"

    markdown = KNOWLEDGE_PATH.read_text(encoding="utf-8")
    terms = _query_terms(query)
    scored: list[tuple[int, str]] = []
    for section in _sections(markdown):
        lowered = section.lower()
        score = sum(1 for term in terms if term in lowered)
        if score:
            scored.append((score, section))

    if not scored:
        return f"在 demo 知识库中未找到与“{query}”相关的内容。"

    scored.sort(key=lambda item: item[0], reverse=True)
    matches = [section for _, section in scored[:2]]
    return "来源：knowledge/demo_knowledge.md\n\n" + "\n\n".join(matches)


@tool
def get_demo_knowledge(query: str) -> str:
    """Query the local demo engineering knowledge and demo specification.

    Use this when the user asks about the demo specification, its safety factor,
    assumptions, units, or other information stored in the local knowledge file.
    This is a simple local lookup, not a general web search or RAG system.
    """
    return search_demo_knowledge(query)
