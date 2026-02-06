from fastmcp import FastMCP
from data.models import Customer
from tools.customers_tools import get_customer, list_customers, search_customers

mcp = FastMCP("Customers")

@mcp.tool
def get_customer_tool(customer_id: int):
    """Get a single customer by ID."""
    result = get_customer.invoke({"customer_id": customer_id})
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return result

@mcp.tool
def list_customers_tool():
    """List all customers."""
    result = list_customers.invoke({})
    if result and hasattr(result[0], "model_dump"):
        return [r.model_dump() for r in result]
    return result or []

@mcp.tool
def search_customers_tool(query: str):
    """Search customers by name or email."""
    result = search_customers.invoke({"query": query})
    if result and hasattr(result[0], "model_dump"):
        return [r.model_dump() for r in result]
    return result or []

mcp.run()
