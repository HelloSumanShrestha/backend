from pydantic import BaseModel
from datetime import datetime

class Sales(BaseModel):
    SalesNumber: int
    sellerId: int
    customerId: int
    quantity: int
    salesDate: datetime
    price: float
    productId: int
