from config.database import Base
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, Uuid


class CreditModel(Base):
    __tablename__ = "credit"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    member_id = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    reference = Column(Uuid, unique=True)
    airline_code = Column(String)
    partner_code = Column(String)
    transaction_date = Column(DateTime)
    amount = Column(Integer)
    monthly_spending = Column(Integer)
    
    status = Column(String)

    __table_args__ = (
        UniqueConstraint('reference', name='uix_1'),
    )
