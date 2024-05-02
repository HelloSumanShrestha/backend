from pydantic import BaseModel, Field


class Customer(BaseModel):
    customerId: int = Field(description="Unique identifier for the customer")
    customerName: str = Field(description="Name of the customer")
    customerEmail: str = Field(description="Email address of the customer")
    customerPassword: str = Field(description="Customer's password", exclude=True)
