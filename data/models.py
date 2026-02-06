from pydantic import BaseModel

class Order(BaseModel):
    id: int
    customer_id: int
    status: str
    price: float
    created_at: str

class Customer(BaseModel):
    id: int
    name: str
    email: str
    phone: str

class Inventory(BaseModel):
    id: int
    sku: str
    name: str
    quantity: int
    unit: str
    created_at: str

class Note(BaseModel):
    id: int
    customer_id: int
    order_id: int
    content: str
    created_at: str
