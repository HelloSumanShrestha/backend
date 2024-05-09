from typing import List
from fastapi import APIRouter, Body, HTTPException
import aiomysql
from datetime import datetime

from database.database import close_connection, get_connection
from models.product import Product

router = APIRouter()

def dict_to_product(data):
    if data:
        return Product(**data)
    return None

@router.get("/products", response_model=List[Product], tags=["Products"])
async def get_all_products():
    connection = await get_connection()
    cursor = await connection.cursor()

    try:
        today = datetime.now().strftime('%Y-%m-%d')
        await cursor.execute("SELECT * FROM products WHERE productExpiry > %s", (today,))
        products = await cursor.fetchall()
        return [dict_to_product(product) for product in products]

    except aiomysql.Error as err:
        print(f"Error retrieving products: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        await close_connection(connection)

@router.get("/products/{product_id}", response_model=Product, tags=["Products"])
async def get_product(product_id: int):
    connection = await get_connection()
    cursor = await connection.cursor()

    try:
        today = datetime.now().strftime('%Y-%m-%d')
        await cursor.execute("SELECT * FROM products WHERE productId = %s AND productExpiry > %s", (product_id, today))
        product = await cursor.fetchone()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return dict_to_product(product)

    except aiomysql.Error as err:
        print(f"Error retrieving product: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        await close_connection(connection)

@router.get("/products/{seller_id}", response_model=List[Product], tags=["Products"])
async def get_products_by_seller(seller_id: int):
    connection = await get_connection()
    cursor = await connection.cursor()

    try:
        today = datetime.now().strftime('%Y-%m-%d')
        await cursor.execute("SELECT * FROM products WHERE sellerId = %s AND productExpiry > %s", (seller_id, today))
        products = await cursor.fetchall()

        if not products:
            raise HTTPException(status_code=404, detail="No products found for the seller")

        return [dict_to_product(product) for product in products]

    except aiomysql.Error as err:
        print(f"Error retrieving products: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        await close_connection(connection)

@router.post("/products/create", response_model=Product, tags=["Products"])
async def create_product(product: Product = Body(...)):
    connection = await get_connection()
    cursor = await connection.cursor()

    try:
        sql = """
            INSERT INTO products (
                productName, productQuantity, productImage, productPrice,
                productMake, productExpiry, productCategory, sellerId, sold
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        await cursor.execute(sql, (
            product.productName,
            product.productQuantity,
            product.productImage,
            product.productPrice,
            product.productMake,
            product.productExpiry,
            product.productCategory,
            product.sellerId,
            product.sold
        ))

        await connection.commit()

        product_id = cursor.lastrowid

        # Fetch the newly created product
        await cursor.execute("SELECT * FROM products WHERE productId = %s", (product_id,))
        new_product = await cursor.fetchone()

        if not new_product:
            raise HTTPException(status_code=404, detail="Newly created product not found")

        return dict_to_product(new_product)

    except aiomysql.Error as err:
        print(f"Error creating product: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        await close_connection(connection)

@router.put("/products/{product_id}", response_model=Product, tags=["Products"])
async def update_product(product_id: int, product: Product = Body(...)):
    connection = await get_connection()
    cursor = await connection.cursor()

    try:
        sql = """
            UPDATE products SET
                productName = %s,
                productQuantity = %s,
                productImage = %s,
                productPrice = %s,
                productMake = %s,
                productExpiry = %s,
                productCategory = %s,
                sellerId = %s,
                sold = %s
            WHERE productId = %s
        """

        await cursor.execute(sql, (
            product.productName,
            product.productQuantity,
            product.productImage,
            product.productPrice,
            product.productMake,
            product.productExpiry,
            product.productCategory,
            product.sellerId,
            product.sold,
            product_id
        ))

        await connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        return await get_product(product_id)

    except aiomysql.Error as err:
        print(f"Error updating product: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        await close_connection(connection)

@router.delete("/products/{product_id}", response_model=dict, tags=["Products"])
async def delete_product(product_id: int):
    connection = await get_connection()
    cursor = await connection.cursor()

    try:
        await cursor.execute("DELETE FROM products WHERE productId = %s", (product_id,))

        await connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        return {"message": "Product deleted successfully"}

    except aiomysql.Error as err:
        print(f"Error deleting product: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        await close_connection(connection)


@router.get("/products/category/{category}", response_model=List[Product], tags=["Category"])
async def get_products_by_category(category: str):
    connection = await get_connection()
    cursor = await connection.cursor()

    try:
        today = datetime.now().strftime('%Y-%m-%d')
        await cursor.execute("SELECT * FROM products WHERE productCategory = %s AND productExpiry >= %s", (category, today))
        products = await cursor.fetchall()

        if not products:
            raise HTTPException(status_code=404, detail="No products found for the category")

        return [dict_to_product(product) for product in products]

    except aiomysql.Error as err:
        print(f"Error retrieving products by category: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        await close_connection(connection)


@router.get("/categories", response_model=List[str], tags=["Category"])
async def get_categories():
    connection = await get_connection()
    cursor = await connection.cursor()

    try:
        await cursor.execute("SELECT DISTINCT productCategory FROM products")
        categories = await cursor.fetchall()

        if not categories:
            return []

        return [category[0] for category in categories if category and category[0]]

    except aiomysql.Error as err:
        print(f"Error retrieving categories: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        await close_connection(connection)



