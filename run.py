"""EngiAgent command-line entry point."""

from engi_agent.agent import EngiAgent
from engi_agent.config import ConfigurationError


def main() -> None:
    print("EngiAgent CLI")
    print("Type 'exit' or 'quit' to leave.\n")

    try:
        agent = EngiAgent()
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}")
        return

    while True:
        try:
            user_input = input("User: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            return
        if not user_input:
            continue

        try:
            response = agent.run_turn(user_input)
        except Exception as exc:  # Keep the educational CLI usable on API errors.
            print(f"Assistant error: {exc}\n")
            continue

        for event in response.tool_events:
            print(event)
        print(f"Assistant: {response.content}\n")


if __name__ == "__main__":
    main()
