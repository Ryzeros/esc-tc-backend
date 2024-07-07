from models.promotions import PromotionModel
from schemas.promotions import PromotionBase
from utils.service_result import ServiceResult
from services.main import AppService, AppCRUD
from utils.app_exceptions import AppException


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
            multiplier=item.multiplier,
            expiry=item.expiry,
            rules=item.rules
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
