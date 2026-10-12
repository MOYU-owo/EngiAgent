"""Live DeepSeek smoke checks for the five MVP behaviors.

This script makes paid network requests and is intentionally separate from the
offline pytest suite. It requires a valid DEEPSEEK_API_KEY in .env.
"""

from uuid import uuid4

from engi_agent.agent import EngiAgent


def tool_names(events: list[str]) -> set[str]:
    names = set()
    for event in events:
        if event.startswith("[Tool call] "):
            names.add(event.removeprefix("[Tool call] ").split("(", 1)[0])
    return names


def print_case_result(
    label: str,
    user_inputs: list[str],
    tool_events: list[str],
    final_answer: str,
) -> None:
    """Print the evidence required for a manual live-test review."""
    actual_tools = tool_names(tool_events)
    print(f"\n{label}")
    for index, user_input in enumerate(user_inputs, start=1):
        suffix = f"（第 {index} 轮）" if len(user_inputs) > 1 else ""
        print(f"用户输入{suffix}: {user_input}")
    print(f"是否调用 Tool: {'是' if actual_tools else '否'}")
    print(f"Tool 名称: {', '.join(sorted(actual_tools)) if actual_tools else '无'}")
    if tool_events:
        print("Tool 参数与结果:")
        for event in tool_events:
            print(f"  {event}")
    else:
        print("Tool 参数与结果: 无")
    print(f"最终回答: {final_answer}")
    print("是否通过: PASS")


def run_single_turn_cases() -> None:
    cases = [
        ("case 1: chat", "你好，请用一句话介绍你自己。", set()),
        ("case 2: calculator", "计算 12.5 × 8。", {"calculator"}),
        (
            "case 3: knowledge",
            "demo 规范中的安全系数是多少？",
            {"get_demo_knowledge"},
        ),
        (
            "case 4: combined",
            "计算 12.5 × 8，同时告诉我 demo 规范中的安全系数。",
            {"calculator", "get_demo_knowledge"},
        ),
    ]

    for label, prompt, expected_tools in cases:
        agent = EngiAgent(thread_id=f"live-{uuid4()}")
        response = agent.run_turn(prompt)
        actual_tools = tool_names(response.tool_events)
        assert actual_tools == expected_tools, (
            f"{label}: expected tools {expected_tools}, got {actual_tools}"
        )
        print_case_result(label, [prompt], response.tool_events, response.content)


def run_memory_case() -> None:
    agent = EngiAgent(thread_id=f"live-memory-{uuid4()}")
    first = agent.run_turn("记住当前项目跨度是 6m。只需简短确认。")
    second = agent.run_turn("刚才的跨度是多少？")

    assert "6" in second.content and "m" in second.content.lower(), second.content
    assert not first.tool_events and not second.tool_events
    print_case_result(
        "case 5: short-term memory",
        ["记住当前项目跨度是 6m。只需简短确认。", "刚才的跨度是多少？"],
        [*first.tool_events, *second.tool_events],
        second.content,
    )


def main() -> None:
    run_single_turn_cases()
    run_memory_case()
    print("All live DeepSeek smoke cases passed.")


if __name__ == "__main__":
    main()
