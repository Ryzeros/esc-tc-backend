from fastapi import APIRouter, Depends
from services.credit import CreditService
from schemas.credit import CreditItem, CreditCreate, CreditItems, CreditBoolean
from utils.service_result import handle_result
from config.database import get_db
from utils.credentials_misc import require_role
from models.user import UserModel

router = APIRouter(
    prefix="/credit",
    tags=["credit"],
)


@router.post("/get_all/", response_model=list[CreditItems])
async def get_item(member_id: str, current_user: UserModel = Depends(require_role("partner")), db: get_db = Depends()):
    result = CreditService(db).get_items(member_id)
    return handle_result(result)


@router.post("/get/", response_model=CreditItem)
async def get_item(reference: str, current_user: UserModel = Depends(require_role("partner")), db: get_db = Depends()):
    result = CreditService(db).get_item(reference)
    return handle_result(result)


@router.post("/add/", response_model=CreditItem)
async def add_item(item: CreditCreate, current_user: UserModel = Depends(require_role("partner")), db: get_db = Depends()):
    result = CreditService(db).add_item(item)
    return handle_result(result)


@router.post("/delete/", response_model=CreditBoolean)
async def delete_credits(email: str, partner_code: str, current_user: UserModel = Depends(require_role("partner")),
                         db: get_db = Depends()):
    result = CreditService(db).delete_item(email, partner_code)
    return handle_result(result)


@router.post("/get_by_email/", response_model=list[CreditItems])
async def get_item(email: str, partner_code: str, current_user: UserModel = Depends(require_role("partner")),
                   db: get_db = Depends()):
    result = CreditService(db).get_items_by_email(email, partner_code)
    return handle_result(result)
