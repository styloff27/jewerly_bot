from fastmcp import FastMCP
from tools.notes_tools import get_note, list_notes_for_customer, list_notes_for_order, add_note

mcp = FastMCP("Notes")

@mcp.tool
def get_note_tool(customer_id: int, order_id: int):
    """Get a note by customer ID and order ID."""
    result = get_note.invoke({"customer_id": customer_id, "order_id": order_id})
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return result

@mcp.tool
def list_notes_for_customer_tool(customer_id: int):
    """List all notes for a customer."""
    result = list_notes_for_customer.invoke({"customer_id": customer_id})
    if result and hasattr(result[0], "model_dump"):
        return [r.model_dump() for r in result]
    return result or []

@mcp.tool
def list_notes_for_order_tool(order_id: int):
    """List all notes for an order."""
    result = list_notes_for_order.invoke({"order_id": order_id})
    if result and hasattr(result[0], "model_dump"):
        return [r.model_dump() for r in result]
    return result or []

@mcp.tool
def add_note_tool(customer_id: int, order_id: int, content: str, confirmed: bool = False):
    """Add a note to a customer and order."""
    if not confirmed:
        return (
            "CONFIRM_REQUIRED: Please confirm the note addition."
            f"Ask the user: 'Are you sure you want to add a note to the customer {customer_id} and order {order_id}? (yes/no)'"
            "If the user say yes, call this tool again with confirmed=True"
            "If the user say no, return the note as is"
            "If the user say anything else, return an error"
        )
    result = add_note.invoke({"customer_id": customer_id, "order_id": order_id, "content": content, "confirmed": confirmed})
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return result

mcp.run()
