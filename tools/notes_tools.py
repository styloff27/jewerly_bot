from langchain_core.tools import tool
from data.db import get_connection
from data.models import Note

@tool
def get_note(customer_id: int, order_id: int) -> Note:
    """Get note by customer ID and order ID."""
    with get_connection() as conn:
        try:
            row = conn.execute("SELECT * FROM notes WHERE customer_id = ? AND order_id = ?", (customer_id, order_id)).fetchone()
            if row is None:
                return {"error": "Note not found"}
            return Note.model_validate(dict(row))
        except Exception as e:
            raise ValueError(f"Error getting note: {str(e)}")

@tool
def list_notes_for_order(order_id: int) -> list[Note]:
    """List all notes for an order."""
    with get_connection() as conn:
        try:
            rows = conn.execute("SELECT * FROM notes WHERE order_id = ?", (order_id,)).fetchall()
            return [Note.model_validate(dict(row)) for row in rows]
        except Exception as e:
            raise ValueError(f"Error listing notes for order: {str(e)}")

@tool
def list_notes_for_customer(customer_id: int) -> list[Note]:
    """List all notes for a customer."""
    with get_connection() as conn:
        try:
            rows = conn.execute("SELECT * FROM notes WHERE customer_id = ?", (customer_id,)).fetchall()
            return [Note.model_validate(dict(row)) for row in rows]
        except Exception as e:
            raise ValueError(f"Error listing notes for customer: {str(e)}")

@tool
def add_note(customer_id: int, order_id: int, content: str, confirmed: bool = False) -> Note:
    """Add a note to a customer or order."""
    if not confirmed:
        return (
            "CONFIRM_REQUIRED: Please confirm the note addition."
            f"Ask the user: 'Are you sure you want to add a note to the customer {customer_id} and order {order_id}? (yes/no)'"
            "If user does not provide a customer ID or order ID, ask user to provide one"
            "If the user say yes, call this tool again with confirmed=True"
            "If the user say no, return the note as is"
            "If the user say anything else, return an error"
        )
    content = content.strip()
    if not content:
        return "ERROR: Note content cannot be empty. Please provide a valid note content."
    with get_connection() as conn:
        try:
            conn.execute("INSERT INTO notes (customer_id, order_id, content) VALUES (?, ?, ?)", (customer_id, order_id, content))
            conn.commit()
            return f"Note added to customer {customer_id} and order {order_id}"
        except Exception as e:
            raise ValueError(f"Error adding note: {str(e)}")