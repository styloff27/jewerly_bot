import asyncio
from agent.core import (
    create_agent,
    run_agent,
    load_mcp_tools,
    CUSTOM_TOOLS,
    _is_confirmation,
    _is_rejection,
)


async def main():
    print("Jewelry Ops Agent CLI. Type 'Ctrl+C' to exit.")
    mcp_tools = await load_mcp_tools()
    tools = mcp_tools + CUSTOM_TOOLS
    executor = create_agent(max_iterations=25, tools=tools)
    chat_history = []
    pending_action = None

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue

            # Decide what to send to the agent based on whether we're waiting for confirmation
            if pending_action is not None:
                if _is_confirmation(user_input):
                    input_to_agent = (
                        f"User said: {user_input}\n\n"
                        "[System: The user confirmed. Call the tool "
                        f"'{pending_action['tool']}' with these arguments (confirmed=True): "
                        f"{pending_action['args']}. Execute it now.]"
                    )
                    pending_action = None
                elif _is_rejection(user_input):
                    input_to_agent = (
                        f"User said: {user_input}. They rejected the pending action. "
                        "Acknowledge and do not perform the action."
                    )
                    pending_action = None
                else:
                    input_to_agent = user_input
            else:
                input_to_agent = user_input

            result = await run_agent(executor, input_to_agent, chat_history)
            print("Assistant:", result["output"])

            if result["pending_confirmation"]:
                pending_action = result.get("pending_action")
                print("Please confirm the action before continuing (yes/no).")

            chat_history.append((
                user_input,
                result["output"],
                result.get("intermediate_steps", []),
            ))
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    asyncio.run(main())
