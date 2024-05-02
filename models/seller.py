from pydantic import BaseModel, Field

class Seller(BaseModel):
    sellerId: int = Field(description="Unique identifier for the seller")
    sellerName: str = Field(description="Name of the seller")
    sellerEmail: str = Field(description="Email address of the seller")
    sellerPassword: str = Field(description="Seller's password", hidden=True)
