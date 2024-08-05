from fastapi import APIRouter, Depends
from utils.service_result import handle_result
from config.database import get_db
from schemas.promotions import PromotionBase, GetPromotionResponse, PromotionNameDescription, GetPromotionRequest
from services.promotions import PromotionService
from utils.credentials_misc import require_role
from models.user import UserModel

router = APIRouter(
    prefix="/promotions",
    tags=['promotions']
)


@router.post("/get_by_partner_id/", response_model=list[GetPromotionResponse])
async def get_all_promotions(current_user: UserModel = Depends(require_role("partner")), db: get_db = Depends()):
    result = PromotionService(db).get_all_promotions_partner(current_user.partner_code)
    return handle_result(result)


@router.post("/add", response_model=GetPromotionResponse)
async def add_promotion(item: PromotionBase, current_user: UserModel = Depends(require_role("admin")),
                        db: get_db = Depends()):
    result = PromotionService(db).add_item(item)
    return handle_result(result)


@router.post("/get_by_id/", response_model=GetPromotionResponse)
async def get_promotion_by_id(item: GetPromotionRequest, current_user: UserModel = Depends(require_role("partner")),
                              db: get_db = Depends()):
    result = PromotionService(db).get_promotion_by_id(item.id)
    return handle_result(result)


@router.post("/get_name_description", response_model=list[PromotionNameDescription])
async def get_all_promotion_names(current_user: UserModel = Depends(require_role("partner")),
                                  db: get_db = Depends()):
    result = PromotionService(db).get_all_promotion_names(current_user.partner_code)
    return handle_result(result)
