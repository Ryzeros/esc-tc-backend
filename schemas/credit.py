from datetime import date, datetime
from pydantic import BaseModel
from config.database import get_db
from typing import Any
from uuid import UUID


class CreditBase(BaseModel):
    member_id: str
    amount: int


class CreditCreate(CreditBase):
    first_name: str
    last_name: str
    airline_code: str
    partner_code: str
    email: str
    additional_info: dict[str, Any]


class CreditItems(CreditBase):
    status: str
    airline_code: str
    reference: UUID
    transaction_date: datetime

    class Config:
        from_attributes = True


class CreditItem(CreditItems):
    first_name: str
    last_name: str
