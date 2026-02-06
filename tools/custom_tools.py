"""Custom tools for agent decision-making: summarization, entity extraction, confirmation checks."""

import re
from langchain_core.tools import tool


@tool
def summarize_conversation_state(recent_tool_calls: str, conversation_state: str) -> str:
    """Summarize the current agent state and conversation in 1-3 sentences.
    Use when you have many tool results or turns and need to refocus on what the user wants,
    what has been done, and what is still pending (e.g. confirmation, next step).
    Inputs: recent_tool_calls = what tools were called and their outcomes; conversation_state = recent user/assistant messages."""
    if not conversation_state or not conversation_state.strip():
        if recent_tool_calls and recent_tool_calls.strip():
            return f"Tool activity so far: {recent_tool_calls.strip()[:400]}."
        return "No conversation or tool activity to summarize yet."
    conv = conversation_state.strip()[:600]
    if recent_tool_calls and recent_tool_calls.strip():
        tools_part = recent_tool_calls.strip()[:300]
        return f"Recent conversation: {conv} | Tool results: {tools_part}"
    return f"Recent conversation: {conv}"

@tool
def extract_entities(user_message: str) -> str:
    """Extract order IDs, customer names, and SKUs from the user's message.
    Use when the user mentions an order, customer, or product and you need to know which IDs/names to use for tool calls.
    Returns a single line like: order_ids: [2, 4], customer_ids: [1, 2], skus: [RING-001].
    Input: the raw user message (or the latest user turn)."""
    if not user_message:
        return "ERROR: User message cannot be empty. Please provide a valid user message."
    order_ids = list(set(re.findall(r"order(?:s)?\s*#?\s*(\d+)", user_message, re.I)))
    customer_ids = list(set(re.findall(r"customer(?:s)?(?:_id)?\s*#?\s*(\d+)", user_message, re.I)))
    sku_like = list(set(re.findall(r"\b[A-Z]{3,4}-\d{3}\b", user_message, re.I)))
    parts = []
    if order_ids:
        parts.append("Order IDs: " + ", ".join(sorted(order_ids, key=int)))
    if customer_ids:
        parts.append("Customer IDs: " + ", ".join(sorted(customer_ids, key=int)))
    if sku_like:
        parts.append("SKUs: " + ", ".join(sorted(sku_like)))
    if not parts:
        return "No order IDs (e.g. 'order 2'), customer IDs (e.g. 'customer 1'), or SKUs (e.g. RING-001) found."
    return "\n".join(parts)

@tool
def action_requires_confirmation(action_description: str) -> str:
    """Check whether the described action requires explicit user confirmation before doing it.
    Use before calling any tool that changes data (update order status, add note, change inventory).
    Input: short description of the action, e.g. 'update order 2 status to shipped' or 'add note to customer 1'.
    Returns CONFIRM_REQUIRED: <reason> if the user must confirm, or OK: No user confirmation required for read-only actions."""
    if not action_description or not isinstance(action_description, str):
        return "OK: No user confirmation required."
    desc = action_description.strip().lower()
    changing = (
        "update" in desc or "add " in desc or "change" in desc or "mark" in desc
        or "set " in desc or "delete" in desc or "create" in desc or "insert" in desc
        or "modify" in desc or "edit" in desc
    )
    readonly = (
        "get " in desc or "list " in desc or "search" in desc or "find" in desc
        or "show" in desc or "look up" in desc or "check " in desc or "fetch" in desc
    )
    if readonly and not changing:
        return "OK: No user confirmation required (read-only action)."
    if changing:
        return (
            "CONFIRM_REQUIRED: This action changes data. "
            "Ask the user to confirm before calling the tool (e.g. 'Are you sure? (yes/no)'). "
            "Only call the mutating tool again with confirmed=True after the user says yes."
        )
    return "OK: No user confirmation required."
