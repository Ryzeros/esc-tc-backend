from fastapi import APIRouter, Depends
from services.credit import CreditService
from schemas.credit import CreditItem, CreditCreate, CreditItems, CreditEmailBoolean, CreditReferenceBoolean, CreditMember, CreditEmail, CreditReference
from utils.service_result import handle_result
from config.database import get_db
from utils.credentials_misc import require_role
from models.user import UserModel

router = APIRouter(
    prefix="/credit",
    tags=["credit"],
)


@router.post("/get_by_member_id/", response_model=list[CreditItems])
async def get_by_member_id(member_id: CreditMember, current_user: UserModel = Depends(require_role("partner")), db: get_db = Depends()):
    member_id.set_partner_code(current_user.partner_code)
    result = CreditService(db).get_by_member_id(member_id)
    return handle_result(result)


@router.post("/get_by_reference/", response_model=CreditItem)
async def get_by_reference(item: CreditReference, current_user: UserModel = Depends(require_role("partner")), db: get_db = Depends()):
    item.set_partner_code(current_user.partner_code)
    result = CreditService(db).get_item_by_reference(item)
    return handle_result(result)


@router.post("/add/", response_model=CreditItem)
async def add_item(item: CreditCreate, current_user: UserModel = Depends(require_role("partner")), db: get_db = Depends()):
    item.set_partner_code(current_user.partner_code)
    result = CreditService(db).add_item(item)
    return handle_result(result)


@router.post("/delete_by_email/", response_model=CreditEmailBoolean)
async def delete_by_email(item: CreditEmail, current_user: UserModel = Depends(require_role("partner")),
                          db: get_db = Depends()):
    item.set_partner_code(current_user.partner_code)
    result = CreditService(db).delete_by_email(item)
    return handle_result(result)


@router.post("/get_by_email/", response_model=list[CreditItems])
async def get_by_email(item: CreditEmail, current_user: UserModel = Depends(require_role("partner")),
                       db: get_db = Depends()):
    item.set_partner_code(current_user.partner_code)
    result = CreditService(db).get_items_by_email(item)
    return handle_result(result)


@router.post("/delete_by_reference/", response_model=CreditReferenceBoolean)
async def delete_by_reference(item: CreditReference, current_user: UserModel = Depends(require_role("partner")),
                              db: get_db = Depends()):
    item.set_partner_code(current_user.partner_code)
    result = CreditService(db).delete_by_reference(item)
    return handle_result(result)
