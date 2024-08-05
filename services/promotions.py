from typing import List, Type
from sqlalchemy import or_
from models.promotions import PromotionModel
from schemas.promotions import PromotionBase, GetPromotionBasedOnPartner
from utils.service_result import ServiceResult
from services.main import AppService, AppCRUD
from utils.app_exceptions import AppException
from datetime import datetime


class PromotionService(AppService):
    def get_all_promotions_partner(self, partner_code: str) -> ServiceResult:
        item = PromotionCRUD(self.db).get_all_promotions_partner(partner_code)
        if not item:
            return ServiceResult(AppException.GetItem())
        return ServiceResult(item)

    def get_promotion_by_id(self, promotion_id: int) -> ServiceResult:
        item = PromotionCRUD(self.db).get_promotion_by_id(promotion_id)
        if not item:
            return ServiceResult(AppException.GetItem())
        return ServiceResult(item)

    def add_item(self, item: PromotionBase) -> ServiceResult:
        item = PromotionCRUD(self.db).add_items(item)
        if not item:
            return ServiceResult(AppException.AddItem())
        return ServiceResult(item)

    def get_all_promotion_names(self, partner_code: str) -> ServiceResult:
        item = PromotionCRUD(self.db).get_all_promotion_names(partner_code)
        if not item:
            return ServiceResult(AppException.GetItem())
        return ServiceResult(item)


class PromotionCRUD(AppCRUD):
    def get_all_promotions_partner(self, partner_code: str) -> list[Type[PromotionModel]] | None:
        item = self.db.query(PromotionModel).filter(PromotionModel.partner_code == partner_code,
                                                    PromotionModel.expiry > datetime.now()).all()
        if item:
            return item
        return None

    def get_promotion_by_id(self, promotion_id: int) -> PromotionModel | None:
        item = self.db.query(PromotionModel).filter(PromotionModel.id == promotion_id).first()
        if item:
            return item
        return None

    def add_items(self, item: PromotionBase) -> PromotionModel:
        item = PromotionModel(
            airline_code=item.airline_code,
            partner_code=item.partner_code,
            expiry=item.expiry,
            points_rule=item.points_rule,
            conditions=item.conditions,
            name=item.name,
            description=item.description,
            start_date_for_card=item.start_date_for_card,
            end_date_for_card=item.end_date_for_card
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_airline_partner_promotions(self, airline_code: str, partner_code: str) -> list[PromotionModel] | None:
        item = self.db.query(PromotionModel).filter(PromotionModel.airline_code == airline_code,
                                                    PromotionModel.partner_code == partner_code,
                                                    PromotionModel.expiry > datetime.now()).all()
        if item:
            return item
        return None

    def get_all_promotion_names(self, partner_code: str) -> list[PromotionModel] | None:
        item = self.db.query(PromotionModel).filter(PromotionModel.partner_code == partner_code,
                                                    PromotionModel.expiry > datetime.now()).all()
        if item:
            return item
        return None
