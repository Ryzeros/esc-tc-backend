from pydantic import BaseModel
from typing import Optional


class UserToken(BaseModel):
    access_token: str
    token_type: str


class UserTokenData(BaseModel):
    email: Optional[str] = None


class UserRegisterRequest(BaseModel):
    email: str
    password: str
    confirm_password: str


class UserRegisterResponse(BaseModel):
    email: str


class UserResponse(UserRegisterResponse):
    roles: str


class UserLoginRequest(BaseModel):
    email: str
    password: str
