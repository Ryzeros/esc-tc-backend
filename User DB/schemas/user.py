from pydantic import BaseModel


# class UserBase(BaseModel):
#     first_name: str
#     last_name: str
#     username: str
#     class Config:
#         from_attributes = True

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    password: str
    class Config:
        from_attributes = True
