from datetime import datetime
from typing import Any
from pydantic import BaseModel


class PromotionBase(BaseModel):
    id: int
    airline_code: str
    partner_code: str
    expiry: datetime
    points_rule: dict[str, Any]
    conditions: dict[str, dict[str, Any]]
