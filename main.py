from agent.core import create_agent, run_agent
import asyncio

async def main():
    print("Jewelry Ops Agent CLI. Type 'Ctrl+C' to exit.")
    executor = create_agent(max_iterations=25)
    chat_history = []

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            result = await run_agent(executor, user_input, chat_history)
            print("Assistant:", result["output"])
            if result["pending_confirmation"]:
                print("Please confirm the action before continuing.")
            chat_history.append((user_input, result["output"]))
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    asyncio.run(main())
