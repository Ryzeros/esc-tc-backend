from config.database import Base
from sqlalchemy import Column, String, Integer, Double, DateTime
from sqlalchemy.dialects.postgresql import JSONB


class PromotionModel(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    airline_code = Column(String, nullable=False)
    partner_code = Column(String, nullable=True)
    multiplier = Column(Double, nullable=False)
    expiry = Column(DateTime, nullable=True)
    rules = Column(JSONB, nullable=False)