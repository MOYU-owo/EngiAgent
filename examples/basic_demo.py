"""Minimal one-turn example. Requires DEEPSEEK_API_KEY in .env."""

from engi_agent.agent import EngiAgent


def main() -> None:
    agent = EngiAgent(thread_id="basic-demo")
    response = agent.run_turn(
        "计算 12.5 × 8，同时告诉我 demo 规范中的安全系数。"
    )
    for event in response.tool_events:
        print(event)
    print(response.content)


if __name__ == "__main__":
    main()
