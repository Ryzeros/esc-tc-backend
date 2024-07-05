from config.database import Base
from sqlalchemy import Column, Integer, String, Float


class LoyaltyModel(Base):
    __tablename__ = "loyalty"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    program_id = Column(String, unique=True)
    program_name = Column(String)
    currency_name = Column(String)
    processing_time = Column(String)
    description = Column(String)
    enrollment_link = Column(String)
    terms_link = Column(String)
    regex_pattern = Column(String, nullable=False)
