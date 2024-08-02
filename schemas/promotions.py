from datetime import datetime
from typing import Any
from pydantic import BaseModel, PrivateAttr


class PromotionBase(BaseModel):
    id: int
    name: str
    description: str
    airline_code: str
    partner_code: str
    expiry: datetime
    points_rule: dict[str, Any]
    conditions: dict[str, dict[str, Any]]
    start_date_for_card: datetime
    end_date_for_card: datetime


class GetPromotionRequest(BaseModel):
    id: int


class GetPromotionBasedOnPartner(BaseModel):
    partner_code: str


class PromotionNameDescription(BaseModel):
    name: str
    description: str
