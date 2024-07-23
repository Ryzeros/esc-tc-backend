from fastapi import APIRouter, Depends
from utils.service_result import handle_result
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user import UserToken, UserRegisterResponse, UserRegisterRequest, UserResponse
from config.database import get_db
from services.user import UserService
from models.user import UserModel
from utils.credentials_misc import get_current_active_user


router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.post("/token", response_model=UserToken)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: get_db = Depends()):
    item = UserService(db).authenticate_user(form_data.username, form_data.password)
    return handle_result(item)


@router.post("/signup", response_model=UserRegisterResponse)
async def signup(item: UserRegisterRequest, db: get_db = Depends()):
    item = UserService(db).signup(item)
    return handle_result(item)


@router.post("/me", response_model=UserResponse)
async def read_users_me(current_user: UserModel = Depends(get_current_active_user)):
    return current_user
