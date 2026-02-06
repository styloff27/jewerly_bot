from langchain_core.tools import tool
from data.db import get_connection
from data.models import Customer

@tool
def get_customer(customer_id: int) -> Customer:
    """Get single customer by ID."""
    with get_connection() as conn:
        try:
            row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
            if row is None:
                return {"error": "Customer not found"}
            return Customer.model_validate(dict(row))
        except Exception as e:
            raise ValueError(f"Error getting customer: {str(e)}")

@tool
def list_customers() -> list[Customer]:
    """List all customers."""
    with get_connection() as conn:
        try:
            rows = conn.execute("SELECT * FROM customers").fetchall()
            return [Customer.model_validate(dict(row)) for row in rows]
        except Exception as e:
            raise ValueError(f"Error listing customers: {str(e)}")

@tool
def search_customers(query: str) -> list[Customer]:
    """Search customers by name or email. Use this tool when user wants to find a customer by name or email."""
    query = query.lower().strip()
    if not query:
        return "ERROR: Search query cannot be empty. Please provide a valid search query."
    with get_connection() as conn:
        try:
            rows = conn.execute("SELECT * FROM customers WHERE name LIKE ? OR email LIKE ?", (f"%{query}%", f"%{query}%")).fetchall()
            return [Customer.model_validate(dict(row)) for row in rows]
        except Exception as e:
            raise ValueError(f"Error searching customers: {str(e)}")