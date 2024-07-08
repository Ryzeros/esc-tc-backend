from fastapi import FastAPI
from config.database import create_tables
from routers.user import router as user_router
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

app.include_router(user_router)
