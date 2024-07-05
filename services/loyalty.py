import re

from models.loyalty import LoyaltyModel
from schemas.loyalty import LoyaltyValidate, LoyaltyItem
from utils.service_result import ServiceResult
from services.main import AppService, AppCRUD
from utils.app_exceptions import AppException


class LoyaltyService(AppService):
    def get_all(self) -> ServiceResult:
        item = LoyaltyCRUD(self.db).get_all()
        if not item:
            return ServiceResult(AppException.GetItem())
        return ServiceResult(item)

    def add_item(self, item) -> ServiceResult:
        item = LoyaltyCRUD(self.db).add_item(item)
        if not item:
            return ServiceResult(AppException.AddItem())
        return ServiceResult(item)


class LoyaltyCRUD(AppCRUD):
    def get_all(self) -> LoyaltyModel:
        item = self.db.query(LoyaltyModel).all()
        if item:
            return item
        return None

    def add_item(self, item: LoyaltyValidate) -> LoyaltyItem:
        item = LoyaltyModel(program_id=item.program_id,
                            program_name=item.program_name,
                            currency_name=item.currency_name,
                            processing_time=item.processing_time,
                            description=item.description,
                            enrollment_link=item.enrollment_link,
                            terms_link=item.terms_link,
                            regex_pattern=item.regex_pattern)

        if self.db.query(LoyaltyModel).filter(LoyaltyModel.program_id == item.program_id).first():
            return None

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
