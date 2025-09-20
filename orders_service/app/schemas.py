from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"

class OrderProductBase(BaseModel):
    product_id: int
    quantity: int

class OrderProductCreate(OrderProductBase):
    pass

class OrderProductRead(OrderProductBase):
    id: int
    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    user_id: int
    products: List[OrderProductCreate]

class OrderCreate(OrderBase):
    pass

class OrderRead(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: OrderStatus
    products: List[OrderProductRead]
    class Config:
        orm_mode = True
