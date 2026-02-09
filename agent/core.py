import os
from dotenv import load_dotenv
load_dotenv()

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents.tool_calling_agent.base import create_tool_calling_agent
from langchain_classic.agents.agent import AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
from agent.prompts import SYSTEM_PROMPT
from tools.customers_tools import get_customer, list_customers, search_customers
from tools.orders_tools import get_order, list_orders, update_order_status
from tools.inventories_tools import get_inventory, list_inventory
from tools.notes_tools import get_note, add_note, list_notes_for_order, list_notes_for_customer
from tools.custom_tools import summarize_conversation_state, extract_entities, action_requires_confirmation

from pathlib import Path

PROJECT_ROOT = str(Path(__file__).parent.parent.absolute())
CUSTOM_TOOLS = [summarize_conversation_state, extract_entities, action_requires_confirmation]

CONFIRM_WORDS = ("yes", "y", "ok", "confirm")
REJECT_WORDS = ("no", "n", "cancel")


def _is_confirmation(msg: str) -> bool:
    return msg.strip().lower() in CONFIRM_WORDS


def _is_rejection(msg: str) -> bool:
    return msg.strip().lower() in REJECT_WORDS


def _format_steps_summary(steps: list) -> str:
    """Format intermediate_steps for inclusion in chat context (truncated)."""
    if not steps:
        return ""
    lines = []
    for action, observation in steps:
        tool = getattr(action, "tool", "?")
        inp = getattr(action, "tool_input", "")
        obs = str(observation)
        if len(obs) > 300:
            obs = obs[:300] + "..."
        lines.append(f"- {tool}({inp}) -> {obs}")
    return "\n".join(lines)


async def load_mcp_tools():
    client = MultiServerMCPClient(
        {
            "customers": {
                "command": "uv",
                "args": ["run", "python", "-m", "mcp_servers.customers_server"],
                "transport": "stdio",
                "cwd": PROJECT_ROOT,
            },
            "orders_inventory": {
                "command": "uv",
                "args": ["run", "python", "-m", "mcp_servers.orders_inventory_server"],
                "transport": "stdio",
                "cwd": PROJECT_ROOT,
            },
            "notes": {
                "command": "uv",
                "args": ["run", "python", "-m", "mcp_servers.notes_server"],
                "transport": "stdio",
                "cwd": PROJECT_ROOT,
            },
        },
        tool_name_prefix=True,  # avoids name collisions
    )
    return await client.get_tools()

def create_agent(max_iterations: int = 10, tools: list | None = None):
    if tools is None:
        tools = asyncio.run(load_mcp_tools()) + CUSTOM_TOOLS
    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-2.0-flash",
    #     temperature=0.0,
    #     max_retries=6,
    #     requests_per_second=0.5,
    #     api_key=os.getenv("GEMINI_API_KEY"),
    # )

    llm = ChatOllama(
        model="qwen2.5",
        temperature=0.0,
        base_url="http://localhost:11434",
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )

    executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=max_iterations,
        return_intermediate_steps=True,
    )
    return executor

async def run_agent(
    executor: AgentExecutor,
    user_input: str,
    chat_history: list[tuple] | None = None,
):
    """chat_history: list of (user_text, assistant_text) or (user_text, assistant_text, intermediate_steps)."""
    if chat_history is None:
        chat_history = []

    messages = []
    for entry in chat_history:
        if len(entry) == 3:
            human, ai, steps = entry
        else:
            human, ai = entry[0], entry[1]
            steps = []
        messages.append(HumanMessage(content=human))
        if steps:
            summary = _format_steps_summary(steps)
            if summary:
                messages.append(
                    AIMessage(content=f"[Previous turn tool results:\n{summary}]")
                )
        messages.append(AIMessage(content=ai))

    result = await executor.ainvoke({
        "input": user_input,
        "chat_history": messages,
    })
    output = result.get("output", {"text": "Agent did not return a response."})

    steps = result.get("intermediate_steps", [])
    pending_confirmation = False
    pending_action = None
    for action, observation in steps:
        if "CONFIRM_REQUIRED" in str(observation):
            pending_confirmation = True
            args = (
                dict(action.tool_input)
                if isinstance(getattr(action, "tool_input", None), dict)
                else {}
            )
            args["confirmed"] = True
            pending_action = {
                "tool": getattr(action, "tool", ""),
                "args": args,
            }
    return {
        "output": output,
        "pending_confirmation": pending_confirmation,
        "pending_action": pending_action,
        "intermediate_steps": steps,
    }
