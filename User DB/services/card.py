from models.card import CardModel
from schemas.card import CardBase, CardTC, CardAdd
from utils.service_result import ServiceResult
from services.main import AppService, AppCRUD
from utils.app_exceptions import AppException
from sqlalchemy.exc import IntegrityError
from datetime import datetime


class CardService(AppService):

    # FOR DEBUGGING!!! REMOVE BEFORE PROD
    def get_all_cards(self) -> ServiceResult:
        item = CardCRUD(self.db).get_all_cards()
        if not item:
            return ServiceResult(AppException.GetItem({"error": "Nothing in DB"}))
        return ServiceResult(item)
    

    def get_cards(self, user_id: int) -> ServiceResult:
        item = CardCRUD(self.db).get_cards(user_id)
        if not item:
            return ServiceResult(AppException.GetItem({"error": "Card not found"}))
        return ServiceResult(item)


    def add_card(self, item: CardAdd) -> ServiceResult:
        item = CardCRUD(self.db).add_card(item)
        if item == 0:
            return ServiceResult(AppException.AddItem({"error": "Duplicate cards"}))
        elif item == 1:
            return ServiceResult(AppException.AddItem({"error": "Error adding card to database"}))
        return ServiceResult(item)



class CardCRUD(AppCRUD):

    # FOR DEBUGGING!!! REMOVE BEFORE PROD
    def get_all_cards(self) -> CardModel:
        item = self.db.query(CardModel).all()
        if item:
            return item
        return None

    def get_cards(self, user_id: int) -> CardModel:
        item = self.db.query(CardModel).filter(CardModel.user_id == user_id).all()
        if item:
            return item
        return None


    def add_card(self, item: CardAdd) -> CardModel:
        check = self.db.query(CardModel).filter(CardModel.card_name == item.card_name, CardModel.user_id == item.user_id).first()
        if check:
            return 0
        else:
            item = CardModel(user_id=item.user_id,
                                card_name=item.card_name,
                                monthly_spending=item.monthly_spending,
                                created_at=datetime.now())
            self.db.add(item)
            try:
                    self.db.commit()
                    self.db.refresh(item)
                    return item
            except IntegrityError:
                    self.db.rollback()
                    return 1
