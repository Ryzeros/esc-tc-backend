from fastapi import FastAPI
from config.database import create_tables
from routers.credit import router as credit_router
from routers.loyalty import router as loyalty_router
<<<<<<< HEAD
=======
from routers.promotions import router as promotion_router
>>>>>>> 5050d1b45ae0fa2bc9a1853759ea3728896d01de
from fastapi.middleware.cors import CORSMiddleware

create_tables()
app = FastAPI()


<<<<<<< HEAD


=======
>>>>>>> 5050d1b45ae0fa2bc9a1853759ea3728896d01de
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD


=======
>>>>>>> 5050d1b45ae0fa2bc9a1853759ea3728896d01de
@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(credit_router)
app.include_router(loyalty_router)
app.include_router(promotion_router)