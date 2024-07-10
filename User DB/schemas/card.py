from pydantic import BaseModel


class CardBase(BaseModel):
    user_id: int
    card_name: str

class CardAdd(BaseModel):
    user_id: int
    card_name: str
    monthly_spending: float

class CardInfo(BaseModel):
    card_name: str
    monthly_spending: float

class CardTC(CardBase):
    card_name: str
    monthly_spending: float

class Card(BaseModel):
    monthly_spending: float