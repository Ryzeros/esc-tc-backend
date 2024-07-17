from models.promotions import PromotionModel
from schemas.promotions import PromotionBase
from utils.service_result import ServiceResult
from services.main import AppService, AppCRUD
from utils.app_exceptions import AppException
from datetime import datetime


class PromotionService(AppService):
    def get_all_promotions(self) -> ServiceResult:
        item = PromotionCRUD(self.db).get_all_promotions()
        if not item:
            return ServiceResult(AppException.GetItem())
        return ServiceResult(item)

    def add_item(self, item: PromotionBase) -> ServiceResult:
        item = PromotionCRUD(self.db).add_items(item)
        if not item:
            return ServiceResult(AppException.AddItem())
        return ServiceResult(item)

    def get_airline_partner_promotions(self, airline_code: str, partner_code: str) -> ServiceResult:
        item = PromotionCRUD(self.db).get_airline_partner_promotions(airline_code, partner_code)
        if not item:
            return item
        return ServiceResult(item)


class PromotionCRUD(AppCRUD):
    def get_all_promotions(self) -> PromotionModel:
        item = self.db.query(PromotionModel).all()
        if item:
            return item
        return None

    def add_items(self, item: PromotionBase) -> PromotionModel:
        item = PromotionModel(
            airline_code=item.airline_code,
            partner_code=item.partner_code,
            expiry=item.expiry,
            points_rule=item.points_rule,
            conditions=item.conditions
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_airline_partner_promotions(self, airline_code: str, partner_code: str) -> PromotionModel:
        item = self.db.query(PromotionModel).filter(PromotionModel.airline_code == airline_code,
                                                    PromotionModel.partner_code == partner_code,
                                                    PromotionModel.expiry > datetime.now()).all()
        if item:
            return item
        return None
