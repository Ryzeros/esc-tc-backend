from datetime import date, datetime
from pydantic import BaseModel, field_validator
from config.database import get_db
from typing import Any


class CreditBase(BaseModel):
    member_id: str
    amount: int


class CreditCreate(CreditBase):
    first_name: str
    last_name: str
    airline_code: str
    partner_code: str
    email: str


class CreditItems(CreditBase):
    status: str
    airline_code: str
    reference: str

    class Config:
        from_attributes = True


class CreditItem(CreditItems):
    first_name: str
    last_name: str
