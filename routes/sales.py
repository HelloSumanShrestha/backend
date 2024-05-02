import aiomysql
from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List
from database.database import get_connection
from models.sales import Sales

router = APIRouter()

@router.post("/sales/", response_model=Sales, tags=["Sales"])
async def create_sale(sale: Sales, conn=Depends(get_connection)):
    async with conn.cursor() as cursor:
        try:
            # Insert the sale record
            await cursor.execute(
                "INSERT INTO sales (sellerId, customerId, quantity, salesDate, price, productId) VALUES (%s, %s, %s, %s, %s, %s)",
                (sale.sellerId, sale.customerId, sale.quantity, sale.salesDate, sale.price, sale.productId)
            )
            await conn.commit()

            # Update the product quantity
            await cursor.execute(
                "UPDATE products SET productQuantity = productQuantity - %s WHERE productId = %s",
                (sale.quantity, sale.productId)
            )
            await conn.commit()

            return sale
        except Exception as e:
            await conn.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating sale: {e}")
        

@router.get("/sales/", response_model=List[Sales], tags=["Sales"])
async def get_all_sales(conn=Depends(get_connection)):
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
            await cursor.execute("SELECT * FROM sales")
            return await cursor.fetchall()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving sales: {e}")


@router.get("/sales/{sales_id}", response_model=Sales, tags=["Sales"])
async def get_sales(sales_id: int, conn=Depends(get_connection)):
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
            await cursor.execute("SELECT * FROM sales WHERE SalesNumber = %s", (sales_id,))
            sales = await cursor.fetchone()
            if not sales:
                raise HTTPException(status_code=404, detail="Sales not found")
            return sales
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving sales: {e}")


@router.get("/sales/seller/{seller_id}", response_model=List[Sales], tags=["Sales"])
async def get_sales_by_seller(seller_id: int, conn=Depends(get_connection)):
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
            await cursor.execute("SELECT * FROM sales WHERE sellerId = %s", (seller_id,))
            sales = await cursor.fetchall()
            return sales
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving sales: {e}")


@router.get("/sales/customer/{customer_id}", response_model=List[Sales], tags=["Sales"])
async def get_sales_by_customer(customer_id: int, conn=Depends(get_connection)):
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
            await cursor.execute("SELECT * FROM sales WHERE customerId = %s", (customer_id,))
            sales = await cursor.fetchall()
            return sales
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving sales: {e}")