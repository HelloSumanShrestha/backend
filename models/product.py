from datetime import date
from pydantic import BaseModel, Field

class Product(BaseModel):
    productId: int = Field(description="Unique identifier for the product")
    productName: str = Field(description="Name of the product")
    productQuantity: int = Field(description="Number of units available")
    productImage: str = Field(description="URL or path to the product image")
    productPrice: float = Field(description="Price of the product")
    productMake: date = Field(description="Brand or manufacturer of the product")
    productExpiry: date = Field(description="Date of expiry for the product") 
    productCategory: str = Field(description="Category the product belongs to")
    sellerId: int = Field(description="Foreign key referencing a seller table")
    sold: int = Field(description="Sold Quantity")
