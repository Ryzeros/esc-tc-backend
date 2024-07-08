from fastapi import APIRouter, Depends
from utils.service_result import handle_result
from config.database import get_db
from schemas.promotions import PromotionBase
from services.promotions import PromotionService

router = APIRouter(
    prefix="/promotions",
    tags=['promotions']
)


@router.post("/get_all/", response_model=list[PromotionBase])
async def get_all_promotions(db: get_db = Depends()):
    result = PromotionService(db).get_all_promotions()
    return handle_result(result)


@router.post("/add", response_model=PromotionBase)
async def get_all_promotions(item: PromotionBase, db: get_db = Depends()):
    result = PromotionService(db).add_item(item)
    return handle_result(result)
