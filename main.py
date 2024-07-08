from fastapi import FastAPI
from config.database import create_tables
from routers.credit import router as credit_router
from routers.loyalty import router as loyalty_router
from routers.promotions import router as promotion_router
from fastapi.middleware.cors import CORSMiddleware

create_tables()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(credit_router)
app.include_router(loyalty_router)
app.include_router(promotion_router)