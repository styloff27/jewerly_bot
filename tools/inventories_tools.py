from langchain_core.tools import tool
from data.db import get_connection
from data.models import Inventory

@tool
def get_inventory(sku: str) -> Inventory:
    """Get inventory item by SKU."""
    with get_connection() as conn:
        try:
            row = conn.execute("SELECT * FROM inventory WHERE sku = ?", (sku,)).fetchone()
            if row is None:
                return {"error": "Inventory not found"}
            return Inventory.model_validate(dict(row))
        except Exception as e:
            raise ValueError(f"Error getting inventory: {str(e)}")

@tool
def list_inventory() -> list[Inventory]:
    """List all inventory items."""
    with get_connection() as conn:
        try:
            rows = conn.execute("SELECT * FROM inventory").fetchall()
            return [Inventory.model_validate(dict(row)) for row in rows]
        except Exception as e:
            raise ValueError(f"Error listing inventory: {str(e)}")

@tool
def update_inventory(sku: str, quantity: int, unit: str, confirmed: bool = False) -> Inventory:
    """Update inventory item by SKU."""
    if not confirmed:
        return (
            "CONFIRM_REQUIRED: Please confirm the inventory update."
            f"Ask the user: 'Are you sure you want to update the inventory item {sku} quantity to {quantity} and unit to {unit}? (yes/no)'"
            "If the user say yes, call this tool again with confirmed=True"
            "If the user say no, return the inventory item as is"
            "If the user say anything else, return an error"
        )
    with get_connection() as conn:
        try:
            conn.execute("UPDATE inventory SET quantity = ?, unit = ? WHERE sku = ?", (quantity, unit, sku))
            conn.commit()
            return f"Inventory item {sku} updated to quantity {quantity} and unit {unit}"
        except Exception as e:
            raise ValueError(f"Error updating inventory: {str(e)}")
