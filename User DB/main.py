from fastapi import FastAPI
from config.database import create_tables
from routers.user import router as user_router

create_tables()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(user_router)
