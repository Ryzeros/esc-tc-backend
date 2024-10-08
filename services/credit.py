from models.credit import CreditModel
from schemas.credit import CreditItem, CreditCreate, CreditEmailBoolean, CreditEmail, CreditReferenceBoolean, CreditReference, CreditMember
from utils.service_result import ServiceResult
from services.main import AppService, AppCRUD
from utils.app_exceptions import AppException
from utils.misc import generate_reference
from sqlalchemy.exc import IntegrityError, DataError
from datetime import datetime
from utils.validators import validate_member_id, validate_airline_code
from services.promotions import PromotionCRUD
from utils.promotion_misc import validate_promotions, eval_points_conditions, calculate_points


class CreditService(AppService):
    def get_by_member_id(self, member_id: CreditMember) -> ServiceResult:
        item = CreditCRUD(self.db).get_by_member_id(member_id)
        if not item:
            return ServiceResult(AppException.GetItem({"member_id": member_id.member_id,
                                                       "airline_code": member_id.airline_code}))
        return ServiceResult(item)

    def get_item_by_reference(self, reference: CreditReference) -> ServiceResult:
        try:
            item = CreditCRUD(self.db).get_item_by_reference(reference)
            if not item:
                return ServiceResult(AppException.GetItem({"reference": reference.reference}))
            return ServiceResult(item)
        except DataError:
            return ServiceResult(AppException.GetItem({"reference": reference.reference}))

    def add_item(self, item: CreditCreate) -> ServiceResult:
        if not validate_airline_code(item.airline_code, self.db):
            return ServiceResult(AppException.InvalidItem({"error": "invalid airline code"}))

        if not validate_member_id(item.member_id, item.airline_code, self.db):
            return ServiceResult(AppException.InvalidItem({"error": "invalid member ID"}))
        item = CreditCRUD(self.db).add_item(item)
        if not item:
            return ServiceResult(AppException.AddItem())
        return ServiceResult(item)

    def get_items_by_email(self, email: CreditEmail) -> ServiceResult:
        item = CreditCRUD(self.db).get_items_by_email(email)
        if not item:
            return ServiceResult(AppException.GetItem({"email": email.email}))
        return ServiceResult(item)

    def delete_by_email(self, item: CreditEmail) -> ServiceResult:
        outcome = CreditCRUD(self.db).delete_by_email(item.email, item.partner_code)
        if not outcome.boolean:
            outcome = outcome.model_dump()
            outcome["message"] = "No records with this email"
            return ServiceResult(AppException.DeleteItem(outcome))
        return ServiceResult(outcome)

    def delete_by_reference(self, item: CreditReference) -> ServiceResult:
        outcome = CreditCRUD(self.db).delete_by_reference(item.reference, item.partner_code)
        if not outcome.boolean:
            outcome = outcome.model_dump()
            outcome["message"] = "No records with this reference"
            return ServiceResult(AppException.DeleteItem(outcome))
        return ServiceResult(outcome)


class CreditCRUD(AppCRUD):
    def get_by_member_id(self, member_id: CreditMember) -> list[CreditModel]:
        item = self.db.query(CreditModel).filter(CreditModel.member_id == member_id.member_id,
                                                 CreditModel.airline_code == member_id.airline_code,
                                                 CreditModel.partner_code == member_id.partner_code).all()
        if item:
            return item
        return None

    def get_items_by_email(self, email: CreditEmail) -> CreditModel:
        item = self.db.query(CreditModel).filter(CreditModel.email == email.email,
                                                 CreditModel.partner_code == email.partner_code).all()
        if item:
            return item
        return None

    def get_item_by_reference(self, reference: CreditReference) -> CreditModel:
        item = self.db.query(CreditModel).filter(CreditModel.reference == reference.reference,
                                                 CreditModel.partner_code == reference.partner_code).first()
        if item:
            return item
        return None

    def add_item(self, item: CreditCreate) -> CreditItem:
        if item.promotion_id is None:
            promotions_items = PromotionCRUD(self.db).get_airline_partner_promotions(airline_code=item.airline_code,
                                                                                     partner_code=item.partner_code)
        else:
            promotions_items = PromotionCRUD(self.db).get_promotion_by_id(promotion_id=item.promotion_id)
            promotions_items = [promotions_items]

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

        if promotions_items:
            max_point = [item.amount, 0]
            for promo_item in promotions_items:
                if validate_promotions(promo_item.conditions, item.additional_info):
                    for condition, formula in promo_item.points_rule["point_condition"]:
                        if eval_points_conditions(condition, item.amount):
                            points = int(calculate_points(item.amount, formula))
                            if points > max_point[0]:
                                max_point[0] = points
                                max_point[1] = promo_item.id
                                break
            item.amount = max_point[0]
            item.promotion_id = max_point[1]

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

    def delete_by_email(self, email: str, partner_code: str) -> CreditEmailBoolean:
        rows_del = self.db.query(CreditModel).filter(CreditModel.email == email,
                                                     CreditModel.partner_code == partner_code).delete()
        self.db.commit()
        if rows_del > 0:
            return CreditEmailBoolean(email=email, boolean=True)
        return CreditEmailBoolean(email=email, boolean=False)

    def delete_by_reference(self, reference: str, partner_code: str) -> CreditReferenceBoolean:
        rows_del = self.db.query(CreditModel).filter(CreditModel.reference == reference,
                                                     CreditModel.partner_code == partner_code).delete()
        self.db.commit()
        if rows_del == 1:
            return CreditReferenceBoolean(reference=reference, boolean=True)
        return CreditReferenceBoolean(reference=reference, boolean=False)
