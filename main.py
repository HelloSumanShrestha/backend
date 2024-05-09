from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import customer, products, seller, sales, login

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(customer.router)
app.include_router(seller.router)
app.include_router(sales.router)
app.include_router(login.router)