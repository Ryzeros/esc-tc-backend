from pydantic import BaseModel


class CardBase(BaseModel):
    owned_by: int
    card_name: str

class CardAdd(BaseModel):
    owned_by: int
    card_name: str
    monthly_spending: float

class CardTC(CardBase):
    monthly_spending: float