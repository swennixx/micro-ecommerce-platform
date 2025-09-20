from pydantic import BaseModel
from enum import Enum

class PaymentStatus(str, Enum):
    pending = "pending"
    success = "success"
    failed = "failed"

class PaymentBase(BaseModel):
    order_id: int
    amount: float

class PaymentCreate(PaymentBase):
    pass

class PaymentRead(PaymentBase):
    id: int
    status: PaymentStatus
    class Config:
        orm_mode = True
