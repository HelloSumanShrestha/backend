from fastapi import APIRouter, HTTPException, Depends
import aiomysql
import bcrypt

from database.database import get_connection
from models.customer import Customer

router = APIRouter()

# Function to hash the password
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


# Function to verify the password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# Function to remove password from customer data
def remove_password(customer_data: dict) -> dict:
    if "customerPassword" in customer_data:
        del customer_data["customerPassword"]
    return customer_data


@router.post("/customers/create", response_model=Customer, tags=["Customer"])
async def create_customer(customer: Customer, conn=Depends(get_connection)):
    hashed_password = hash_password(customer.customerPassword)
    async with conn.cursor() as cursor:
        try:
            sql = """
                INSERT INTO customer (customerId, customerName, customerEmail, customerPassword)
                VALUES (%s, %s, %s, %s)
            """
            await cursor.execute(sql, (customer.customerId, customer.customerName, customer.customerEmail, hashed_password))
            await conn.commit()
            return customer
        except aiomysql.Error as err:
            raise HTTPException(status_code=500, detail="Error creating customer")


@router.get("/customers/", response_model=list[Customer], tags=["Customer"])
async def get_customer_list(conn=Depends(get_connection)):
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
            await cursor.execute("SELECT * FROM customer")
            customers = await cursor.fetchall()
            return [Customer(**customer) for customer in customers]
        except aiomysql.Error as err:
            raise HTTPException(status_code=500, detail="Error retrieving customers")

@router.get("/customers/{customer_id}", response_model=Customer, tags=["Customer"])
async def get_customer(customer_id: int, conn=Depends(get_connection)):
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
            await cursor.execute("SELECT * FROM customer WHERE customerId = %s", (customer_id,))
            customer = await cursor.fetchone()
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")
            return Customer(**customer)
        except aiomysql.Error as err:
            raise HTTPException(status_code=500, detail="Error retrieving customer")

# Update a customer
@router.put("/customers/{customer_id}", response_model=Customer, tags=["Customer"])
async def update_customer(customer_id: int, customer: Customer, conn=Depends(get_connection)):
    hashed_password = hash_password(customer.customerPassword)
    async with conn.cursor() as cursor:
        try:
            sql = """
                UPDATE customer SET customerName = %s, customerEmail = %s, customerPassword = %s
                WHERE customerId = %s
            """
            await cursor.execute(sql, (customer.customerName, customer.customerEmail, hashed_password, customer_id))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Customer not found")
            await conn.commit()
            return customer
        except aiomysql.Error as err:
            raise HTTPException(status_code=500, detail="Error updating customer")


# Delete a customer
@router.delete("/customers/{customer_id}", tags=["Customer"])
async def delete_customer(customer_id: int, conn=Depends(get_connection)):
    async with conn.cursor() as cursor:
        try:
            await cursor.execute("DELETE FROM customer WHERE customerId = %s", (customer_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Customer not found")
            await conn.commit()
            return {"message": "Customer deleted successfully"}
        except aiomysql.Error as err:
            raise HTTPException(status_code=500, detail="Error deleting customer")
