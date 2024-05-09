from fastapi import APIRouter, HTTPException, Depends
import bcrypt

from database.database import get_connection
from models.customer import Customer
from models.seller import Seller

router = APIRouter()

# Function to hash the password
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

# Function to verify the password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# Authenticate customer
async def authenticate_customer(customer_email: str, password: str, conn):
    async with conn.cursor() as cursor:
        await cursor.execute("SELECT * FROM customer WHERE customerEmail = %s", (customer_email,))
        customer = await cursor.fetchone()
        if not customer:
            return None
        if not verify_password(password, customer["customerPassword"]):
            return None
        return Customer(**customer)

# Authenticate seller
async def authenticate_seller(seller_email: str, password: str, conn):
    async with conn.cursor() as cursor:
        await cursor.execute("SELECT * FROM seller WHERE sellerEmail = %s", (seller_email,))
        seller = await cursor.fetchone()
        if not seller:
            return None
        if not verify_password(password, seller["sellerPassword"]):
            return None
        return Seller(**seller)

# Login for customer
@router.post("/customers/login",tags=["login"])
async def customer_login(customer_email: str, password: str, conn=Depends(get_connection)):
    customer = await authenticate_customer(customer_email, password, conn)
    if not customer:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"message": "Customer logged in successfully"}

# Login for seller
@router.post("/sellers/login",tags=["login"])
async def seller_login(seller_email: str, password: str, conn=Depends(get_connection)):
    seller = await authenticate_seller(seller_email, password, conn)
    if not seller:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"message": "Seller logged in successfully"}
