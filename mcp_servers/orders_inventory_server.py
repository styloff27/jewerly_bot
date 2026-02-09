from fastmcp import FastMCP
from tools.orders_tools import get_order, list_orders, update_order_status
from tools.inventories_tools import get_inventory, list_inventory, update_inventory

mcp = FastMCP("OrdersInventory")

@mcp.tool
def get_order_tool(order_id: int):
    """Get a single order by ID."""
    result = get_order.invoke({"order_id": order_id})
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return result

@mcp.tool
def list_orders_tool():
    """List all orders."""
    result = list_orders.invoke({})
    if result and hasattr(result[0], "model_dump"):
        return [r.model_dump() for r in result]
    return result or []

@mcp.tool
def update_order_status_tool(order_id: int, status: str, confirmed: bool = False):
    """Update the status of an order."""
    if not confirmed:
        return (
            "CONFIRM_REQUIRED: Please confirm the order status update."
            f"Ask the user: 'Are you sure you want to update the order {order_id} status to {status}? (yes/no)'"
            "If the user say yes, call this tool again with confirmed=True"
            "If the user say no, return the order status as is"
            "If the user say anything else, return an error"
        )
    result = update_order_status.invoke({"order_id": order_id, "status": status, "confirmed": confirmed})
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return result

@mcp.tool
def get_inventory_tool(sku: str):
    """Get a single inventory item by SKU."""
    result = get_inventory.invoke({"sku": sku})
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return result

@mcp.tool
def list_inventory_tool():
    """List all inventory items."""
    result = list_inventory.invoke({})
    if result and hasattr(result[0], "model_dump"):
        return [r.model_dump() for r in result]
    return result or []

@mcp.tool
def update_inventory_tool(sku: str, unit: str, quantity: int, confirmed: bool = False):
    """Update the quantity of an inventory item."""
    if not confirmed:
        return (
            "CONFIRM_REQUIRED: Please confirm the inventory update."
            f"Ask the user: 'Are you sure you want to update the inventory item {sku} unit to {unit} and quantity to {quantity}? (yes/no)'"
            "If the user say yes, call this tool again with confirmed=True"
            "If the user say no, return the inventory item as is"
            "If the user say anything else, return an error"
        )
    result = update_inventory.invoke({"sku": sku, "unit": unit, "quantity": quantity, "confirmed": confirmed})
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return result

mcp.run()
