# main.py
from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

# Create FastAPI instance
app = FastAPI(
    title="My First API",
    description="A simple API for beginners",
    version="1.0.0"
)

# Simple GET endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to my first FastAPI application!", "status": "success"}

# GET endpoint with path parameter
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "query_param": q}

# GET endpoint with query parameters
@app.get("/users/")
def read_users(name: Optional[str] = None, age: Optional[int] = None):
    return {"name": name, "age": age}

# Data model for POST request
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# POST endpoint
@app.post("/items/")
def create_item(item: Item):
    # Calculate total price with tax
    total_price = item.price + (item.tax if item.tax else 0)
    
    return {
        "message": "Item created successfully",
        "item_name": item.name,
        "total_price": total_price,
        "original_data": item.dict()
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "FastAPI Application"}