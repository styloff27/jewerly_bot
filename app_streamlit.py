"""JewelryOps agent Streamlit UI. Chat with the agent; tool calls and confirmations shown."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
load_dotenv()

import asyncio
import streamlit as st
from agent.core import (
    create_agent,
    run_agent,
    load_mcp_tools,
    CUSTOM_TOOLS,
    _is_confirmation,
    _is_rejection,
)


async def main():
    st.set_page_config(page_title="JewelryOps Agent", page_icon="💎", layout="centered")
    st.title("JewelryOps Agent")
    st.caption("Ask about customers, orders, inventory, returns, or draft responses. The agent uses tools and may ask for confirmation before changes.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "pending_action" not in st.session_state:
        st.session_state.pending_action = None
    if "executor" not in st.session_state:
        with st.spinner("Loading agent..."):
            mcp_tools = await load_mcp_tools()
            tools = mcp_tools + CUSTOM_TOOLS
            st.session_state.executor = create_agent(max_iterations=25, tools=tools)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("steps"):
                with st.expander("Tool calls"):
                    for step in msg["steps"]:
                        st.code(step, language="text")

    if prompt := st.chat_input("Your message"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        pending_action = st.session_state.pending_action
        if pending_action is not None:
            if _is_confirmation(prompt):
                input_to_agent = (
                    f"User said: {prompt}\n\n"
                    "[System: The user confirmed. Call the tool "
                    f"'{pending_action['tool']}' with these arguments (confirmed=True): "
                    f"{pending_action['args']}. Execute it now.]"
                )
                st.session_state.pending_action = None
            elif _is_rejection(prompt):
                input_to_agent = (
                    f"User said: {prompt}. They rejected the pending action. "
                    "Acknowledge and do not perform the action."
                )
                st.session_state.pending_action = None
            else:
                input_to_agent = prompt
        else:
            input_to_agent = prompt

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = await run_agent(
                    st.session_state.executor,
                    input_to_agent,
                    st.session_state.chat_history,
                )
            output = result["output"]
            steps = result.get("intermediate_steps", [])
            step_lines = []
            for step in steps:
                action, observation = step[0], step[1]
                tool_name = getattr(action, "tool", str(action))
                tool_input = getattr(action, "tool_input", "")
                step_lines.append(f"Tool: {tool_name}\nInput: {tool_input}\nResult: {str(observation)[:500]}")
            st.markdown(output)
            if result.get("pending_confirmation"):
                st.session_state.pending_action = result.get("pending_action")
                st.info("Agent is waiting for your confirmation. Reply with 'yes' or 'confirm' to approve the action.")
            if step_lines:
                with st.expander("Tool calls"):
                    for line in step_lines:
                        st.code(line, language="text")

        st.session_state.messages.append({
            "role": "assistant",
            "content": output,
            "steps": step_lines,
        })
        st.session_state.chat_history.append((
            prompt,
            output,
            result.get("intermediate_steps", []),
        ))
        st.rerun()  # streamlit >= 1.27


if __name__ == "__main__":
    asyncio.run(main())
