from models.loyalty import LoyaltyModel
from schemas.loyalty import LoyaltyValidate, LoyaltyItem
from utils.service_result import ServiceResult
from services.main import AppService, AppCRUD
from utils.app_exceptions import AppException
import re


class LoyaltyService(AppService):
    def get_all(self) -> ServiceResult:
        item = LoyaltyCRUD(self.db).get_all()
        if not item:
            return ServiceResult(AppException.GetItem())
        return ServiceResult(item)

    def add_item(self, item) -> ServiceResult:
        item = LoyaltyCRUD(self.db).add_item(item)
        if item == "exist":
            return ServiceResult(AppException.AddItem({"message": "Program ID exists"}))
        elif item == "invalid regex":
            return ServiceResult(AppException.AddItem({"message": "Regex Pattern invalid"}))
        return ServiceResult(item)


class LoyaltyCRUD(AppCRUD):
    def get_all(self) -> list[LoyaltyModel] | None:
        item = self.db.query(LoyaltyModel).all()
        if item:
            return item
        return None

    def add_item(self, item: LoyaltyValidate) -> LoyaltyItem | str:
        item = LoyaltyModel(program_id=item.program_id,
                            program_name=item.program_name,
                            currency_name=item.currency_name,
                            processing_time=item.processing_time,
                            description=item.description,
                            enrollment_link=item.enrollment_link,
                            terms_link=item.terms_link,
                            regex_pattern=item.regex_pattern)
        try:
            re.compile(item.regex_pattern)
            if self.db.query(LoyaltyModel).filter(LoyaltyModel.program_id == item.program_id).first():
                return "exist"

            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item

        except re.error:
            return "invalid regex"
