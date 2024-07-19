from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("USERNAME").lower()
PASSWORD = os.getenv("PASSWORD")
URL = os.getenv("URL")
PORT = os.getenv("PORT")

SQLALCHEMY_DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{URL}:{PORT}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
