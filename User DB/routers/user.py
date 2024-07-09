from fastapi import APIRouter, Depends
from services.user import UserService
from schemas.user import UserCreate, UserBase, UserItems, UserItem, UserAuth, UserWithCards
from utils.service_result import handle_result
from config.database import get_db

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.post("/get_all/", response_model=list[UserItems])
async def get_users(db: get_db = Depends()):
    result = UserService(db).get_users()
    return handle_result(result)


@router.post("/get/", response_model=UserWithCards)
async def get_user(user_id: int, db: get_db = Depends()):
    result = UserService(db).get_user(user_id)
    return handle_result(result)

@router.post("/add_user", response_model=UserItems)
async def add_user(item: UserCreate, db: get_db = Depends()):
    result = UserService(db).add_user(item)
    return handle_result(result)

# For user authentication?
@router.post("/auth/", response_model=UserItem)
async def auth_user(item: UserAuth, db: get_db = Depends()):
    result = UserService(db).auth_user(item)
    return handle_result(result)
