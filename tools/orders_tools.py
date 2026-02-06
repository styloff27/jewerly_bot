from data.db import get_connection
from langchain_core.tools import tool
from data.models import Order

@tool
def get_order(order_id: int) -> Order:
    """Get single order by ID."""
    with get_connection() as conn:
        try:
            row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
            if row is None:
                return {"error": "Order not found"}
            return Order.model_validate(dict(row))
        except Exception as e:
            raise ValueError(f"Error getting order: {str(e)}")

@tool
def list_orders() -> list[Order]:
    """List all orders."""
    with get_connection() as conn:
        try:
            rows = conn.execute("SELECT * FROM orders").fetchall()
            return [Order.model_validate(dict(row)) for row in rows]
        except Exception as e:
            raise ValueError(f"Error listing orders: {str(e)}")

@tool
def update_order_status(order_id: int, status: str, confirmed: bool = False) -> Order:
    """Update the status of an order."""
    if not confirmed:
        return (
            "CONFIRM_REQUIRED: Please confirm the order status update."
            f"Ask the user: 'Are you sure you want to update the order {order_id} status to {status}? (yes/no)'"
            "If the user say yes, call this tool again with confirmed=True"
            "If the user say no, return the order status as is"
            "If the user say anything else, return an error"
        )
    status = status.lower().strip()
    with get_connection() as conn:
        try:
            conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
            conn.commit()
            return f"Order {order_id} status updated to {status}"
        except Exception as e:
            raise ValueError(f"Error updating order status: {str(e)}")
