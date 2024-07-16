from models.credit import CreditModel
from schemas.credit import CreditItem, CreditCreate, CreditBoolean
from utils.service_result import ServiceResult
from services.main import AppService, AppCRUD
from utils.app_exceptions import AppException
from utils.misc import generate_reference
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from utils.validators import validate_member_id


class CreditService(AppService):
    def get_items(self, member_id: str) -> ServiceResult:
        item = CreditCRUD(self.db).get_items(member_id)
        if not item:
            return ServiceResult(AppException.GetItem({"member_id": member_id}))
        return ServiceResult(item)

    def get_item(self, reference: str) -> ServiceResult:
        item = CreditCRUD(self.db).get_item(reference)
        if not item:
            return ServiceResult(AppException.GetItem({"reference": reference}))
        return ServiceResult(item)

    def add_item(self, item: CreditCreate) -> ServiceResult:
        if not validate_member_id(item.member_id, item.airline_code, self.db):
            return ServiceResult(AppException.AddItem({"error": "invalid member ID"}))
        item = CreditCRUD(self.db).add_item(item)
        if not item:
            return ServiceResult(AppException.AddItem())
        return ServiceResult(item)

    def get_items_by_email(self, email: str) -> ServiceResult:
        item = CreditCRUD(self.db).get_items_by_email(email)
        if not item:
            return ServiceResult(AppException.GetItem({"email": email}))
        return ServiceResult(item)

    def delete_item(self, email: str, partner_code: str) -> ServiceResult:
        outcome = CreditCRUD(self.db).delete_item(email, partner_code)
        if not outcome.boolean:
            return ServiceResult(AppException.DeleteItem(dict(outcome)))
        return ServiceResult(outcome)


class CreditCRUD(AppCRUD):
    def get_items(self, member_id: str) -> CreditModel:
        item = self.db.query(CreditModel).filter(CreditModel.member_id == member_id).all()
        if item:
            return item
        return None

    def get_items_by_email(self, email: str) -> CreditModel:
        item = self.db.query(CreditModel).filter(CreditModel.email == email).all()
        if item:
            return item
        return None

    def get_item(self, reference: str) -> CreditModel:
        item = self.db.query(CreditModel).filter(CreditModel.reference == reference).first()
        if item:
            return item
        return None

    def add_item(self, item: CreditCreate) -> CreditItem:
        item = CreditModel(member_id=item.member_id,
                           first_name=item.first_name,
                           last_name=item.last_name,
                           transaction_date=datetime.now(),
                           amount=item.amount,
                           email=item.email,
                           airline_code=item.airline_code,
                           partner_code=item.partner_code,
                           status="In Progress",
                           additional_info=item.additional_info)
        for _ in range(5):
            item.reference = generate_reference()
            self.db.add(item)
            try:
                self.db.commit()
                self.db.refresh(item)
                return item
            except IntegrityError:
                self.db.rollback()
                continue
        return None

    def delete_item(self, email: str, partner_code: str) -> CreditBoolean:
        rows_del = self.db.query(CreditModel).filter(CreditModel.email == email, CreditModel.partner_code == partner_code).delete()
        self.db.commit()
        if rows_del > 0:
            return CreditBoolean(email=email, boolean=True)
        return CreditBoolean(email=email, boolean=False)
