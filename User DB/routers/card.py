from fastapi import APIRouter, Depends
from services.card import CardService
from schemas.user import UserCreate, UserBase, UserItems, UserItem, UserAuth
from schemas.card import CardBase, CardTC, CardAdd
from utils.service_result import handle_result
from config.database import get_db

router = APIRouter(
    prefix="/card",
    tags=["card"],
)


@router.post("/get_all/", response_model=list[CardAdd])
async def get_all_cards(db: get_db = Depends()):
    result = CardService(db).get_all_cards()
    return handle_result(result)


@router.post("/get_cards/", response_model=list[CardTC])
async def get_cards(user_id: int, db: get_db = Depends()):
    result = CardService(db).get_cards(user_id)
    return handle_result(result)

@router.post("/add_card", response_model=CardBase)
async def add_card(item: CardAdd, db: get_db = Depends()):
    result = CardService(db).add_card(item)
    return handle_result(result)
