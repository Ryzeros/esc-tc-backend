from datetime import datetime
from typing import Any
from pydantic import BaseModel


class PromotionBase(BaseModel):
    airline_code: str
    partner_code: str
    multiplier: float
    expiry: datetime
    rules: dict[str, Any]
