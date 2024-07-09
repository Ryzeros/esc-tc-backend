from config.database import Base
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)
    cards = relationship("CardModel", back_populates="user")

    __table_args__ = (
        UniqueConstraint('email', name='uix_email'),
        UniqueConstraint('username', name='uix_username'),
    )