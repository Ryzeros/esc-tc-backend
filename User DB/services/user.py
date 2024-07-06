from models.user import UserModel
from schemas.user import UserCreate
from utils.service_result import ServiceResult
from services.main import AppService, AppCRUD
from utils.app_exceptions import AppException
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from utils.validators import validate_email, validate_password


class UserService(AppService):

    # FOR DEBUGGING!!! REMOVE BEFORE PROD
    def get_users(self) -> ServiceResult:
        item = UserCRUD(self.db).get_items()
        if not item:
            return ServiceResult(AppException.GetItem({"error": "Nothing in DB"}))
        return ServiceResult(item)
    

    def get_user(self, username: str) -> ServiceResult:
        item = UserCRUD(self.db).get_user(username)
        if not item:
            return ServiceResult(AppException.GetItem({"username": username}))
        return ServiceResult(item)

    def add_user(self, item: UserCreate) -> ServiceResult:
        if not validate_email(item.email):
            return ServiceResult(AppException.AddItem({"error": "invalid email"}))
        elif not validate_password(item.password):
             return ServiceResult(AppException.AddItem({"error": "invalid password"}))
        item = UserCRUD(self.db).add_user(item)
        if not item:
            return ServiceResult(AppException.AddItem())
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
            return item
        return None

    def add_user(self, item: UserCreate) -> UserModel:
        item = UserModel(first_name=item.first_name,
                           last_name=item.last_name,
                           email=item.email,
                           username=item.username,
                           password=item.password,
                           verified=0,
                           created_at=datetime.now())
        try:
                self.db.commit()
                self.db.refresh(item)
                return item
        except IntegrityError:
                self.db.rollback()
                return None
