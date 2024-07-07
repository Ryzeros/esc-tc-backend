from config.database import Base
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB


class CreditModel(Base):
    __tablename__ = "credit"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    member_id = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone_number = Column()
    reference = Column(Uuid, unique=True)
    airline_code = Column(String)
    partner_code = Column(String)
    transaction_date = Column(DateTime)
    amount = Column(Integer)
    additional_info = Column(JSONB, nullable=True, default={})
    
    status = Column(String)

    __table_args__ = (
        UniqueConstraint('reference', name='uix_1'),
    )
