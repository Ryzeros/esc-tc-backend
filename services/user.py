from services.main import AppService, AppCRUD
from utils.service_result import ServiceResult
from utils.app_exceptions import AppException
from utils.credentials_misc import verify_password, create_access_token, get_password_hash
from models.user import UserModel
from schemas.user import UserToken, UserRegisterRequest
from config.credentials_config import ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta


class UserService(AppService):
    def authenticate_user(self, email: str, password: str) -> ServiceResult:
        user = UserCRUD(self.db).authenticate_user(email, password)
        if not user:
            return ServiceResult(AppException.InvalidAccount())
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"email": email}, expires_delta=access_token_expires)
        user_token = UserToken(
            access_token=access_token,
            token_type="bearer"
        )
        return ServiceResult(user_token)

    def signup(self, item: UserRegisterRequest) -> ServiceResult:
        if not item.password == item.confirm_password:
            return ServiceResult(AppException.InvalidItem({"error": "password and confirm password don't match"}))
        item = UserCRUD(self.db).signup(item)
        if not item:
            return ServiceResult(AppException.AddItem())
        return ServiceResult(item)


class UserCRUD(AppCRUD):
    def authenticate_user(self, email: str, password: str) -> UserModel | None:
        user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if user:
            if verify_password(password, user.password):
                return user
        return None

    def signup(self, item: UserRegisterRequest) -> UserModel:
        if item.roles is None:
            item.roles = "user"
        if "partner" not in item.roles:
            item.partner_code = None
        item = UserModel(
            email=item.email,
            password=get_password_hash(item.password),
            roles=item.roles,
            partner_code=item.partner_code
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
