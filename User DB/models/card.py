from config.database import Base
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship




class CardModel(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    card_name = Column(String(50), nullable=False)
    monthly_spending = Column(Float, nullable=False)
    first_time_use = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    user = relationship("UserModel", back_populates="cards")