from datetime import datetime
from pydantic import BaseModel, PrivateAttr
from typing import Any
from uuid import UUID


class CreditBase(BaseModel):
    member_id: str
    amount: int


class CreditCreate(CreditBase):
    first_name: str
    last_name: str
    airline_code: str
    _partner_code: str = PrivateAttr()
    email: str
    additional_info: dict[str, Any]
    promotion_id: int | None = None

    @property
    def partner_code(self):
        return self._partner_code

    def set_partner_code(self, partner_code: str):
        self._partner_code = partner_code


class CreditItems(CreditBase):
    status: str
    airline_code: str
    reference: UUID
    transaction_date: datetime


class CreditItem(CreditItems):
    first_name: str
    last_name: str


class CreditBoolean(BaseModel):
    email: str
    boolean: bool


class CreditReference(BaseModel):
    reference: str
    _partner_code: str = PrivateAttr()

    @property
    def partner_code(self):
        return self._partner_code

    def set_partner_code(self, partner_code: str):
        self._partner_code = partner_code


class CreditEmail(BaseModel):
    email: str
    _partner_code: str = PrivateAttr()

    @property
    def partner_code(self):
        return self._partner_code

    def set_partner_code(self, partner_code: str):
        self._partner_code = partner_code


class CreditMember(BaseModel):
    member_id: str
    _partner_code: str = PrivateAttr()

    @property
    def partner_code(self):
        return self._partner_code

    def set_partner_code(self, partner_code: str):
        self._partner_code = partner_code
