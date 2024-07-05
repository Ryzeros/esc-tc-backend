from fastapi import FastAPI
from config.database import create_tables
from routers.credit import router as credit_router
from routers.loyalty import router as loyalty_router

create_tables()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(credit_router)
app.include_router(loyalty_router)
