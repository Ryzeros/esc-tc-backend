from models.user import UserModel
from models.card import CardModel
from schemas.user import UserCreate, UserWithCards
from schemas.card import Card
from utils.service_result import ServiceResult
from services.main import AppService, AppCRUD
from utils.app_exceptions import AppException
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from utils.validators import validate_email, validate_password
from utils.misc import hash_password, check_password


class UserService(AppService):

    # FOR DEBUGGING!!! REMOVE BEFORE PROD
    def get_users(self) -> ServiceResult:
        item = UserCRUD(self.db).get_users()
        if not item:
            return ServiceResult(AppException.GetItem({"error": "Nothing in DB"}))
        return ServiceResult(item)
    

    def get_user(self, username: str) -> ServiceResult:
        item = UserCRUD(self.db).get_user(username)
        if not item:
            return ServiceResult(AppException.GetItem({"error": "User not found"}))
        return ServiceResult(item)

    def add_user(self, item: UserCreate) -> ServiceResult:
        if not validate_email(item.email):
            return ServiceResult(AppException.AddItem({"error": "invalid email"}))
        elif not validate_password(item.password):
             return ServiceResult(AppException.AddItem({"error": "invalid password"}))
        item = UserCRUD(self.db).add_user(item)
        if not item:
            return ServiceResult(AppException.AddItem({"error": "Unable to add user"}))
        return ServiceResult(item)

    
    def auth_user(self, item: UserCreate) -> ServiceResult:
        item = UserCRUD(self.db).auth_user(item.username, item.password)
        if not item:
            return ServiceResult(AppException.GetItem({"Error": "Invalid password or user"}))
        return ServiceResult(item)


class UserCRUD(AppCRUD):

    # FOR DEBUGGING!!! REMOVE BEFORE PROD
    def get_users(self) -> UserModel:
        item = self.db.query(UserModel).all()
        if item:
            return item
        return None

    def get_user(self, username: str) -> UserModel:
        item = self.db.query(UserModel).filter(UserModel.username == username).first()
        if item:
            cards_dict = {card.card_name: Card(monthly_spending = card.monthly_spending) for card in item.cards}
            return UserWithCards(
        username=item.username, 
        first_name=item.first_name, 
        last_name=item.last_name,
        email=item.email,
        verified=item.verified, 
        cards=cards_dict
    )
        return None
    
    def auth_user(self, username: str, password: str) -> UserModel:
        item = self.db.query(UserModel).filter(UserModel.username == username).first()
        if check_password(password, item.password):
            return item
        return None


    def add_user(self, item: UserCreate) -> UserModel:
        item = UserModel(first_name=item.first_name,
                           last_name=item.last_name,
                           email=item.email,
                           username=item.username,
                           password=hash_password(item.password),
                           verified=0,
                           created_at=datetime.now())
        self.db.add(item)
        try:
                self.db.commit()
                self.db.refresh(item)
                return item
        except IntegrityError:
                self.db.rollback()
                return None
