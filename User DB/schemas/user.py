from pydantic import BaseModel
from typing import Dict
from schemas.card import Card


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
    cards: Dict[int, Card]

    class Config:
        orm_mode = True