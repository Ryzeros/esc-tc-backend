from pydantic import BaseModel


class UserBase(BaseModel):
    first_name: str
    last_name: str

class UserItems(UserBase):
    verified: bool

    class Config:
        from_attributes = True

class UserItem(UserItems):
    user_id: int
    email: str
    username: str

class UserCreate(UserBase):
    email: str
    username: str
    password: str

class UserAuth(BaseModel):
    username: str
    password: str
