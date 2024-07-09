from pydantic import BaseModel
from schemas.card import Card
from typing import Dict


class UserBase(BaseModel):
    first_name: str
    last_name: str

class UserItems(UserBase):
    verified: bool

    class Config:
        from_attributes = True

class UserItem(UserItems):
    username: str

class UserCreate(UserBase):
    email: str
    username: str
    password: str

class UserAuth(BaseModel):
    username: str
    password: str


class UserWithCards(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    verified: bool
    cards: Dict[str, Card]

    class Config:
        from_attributes = True