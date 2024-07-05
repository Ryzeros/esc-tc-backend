from fastapi import APIRouter, Depends
from schemas.loyalty import LoyaltyItem, LoyaltyValidate
from services.loyalty import LoyaltyService
from utils.service_result import handle_result
from config.database import get_db

router = APIRouter(
    prefix="/loyalty",
    tags=["loyalty"]
)


@router.get("/", response_model=list[LoyaltyItem])
async def get_all(db: get_db = Depends()):
    result = LoyaltyService(db).get_all()
    return handle_result(result)


@router.post("/add", response_model=LoyaltyItem)
async def add(item: LoyaltyValidate, db: get_db = Depends()):
    result = LoyaltyService(db).add_item(item)
    return handle_result(result)
