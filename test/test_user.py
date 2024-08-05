import base64
import binascii
import json
import time
from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from config.database import get_db
from main import app
from models.user import UserModel
from services.user import UserService, UserCRUD
from schemas.user import UserRegisterRequest
from fastapi.exceptions import HTTPException
from utils.credentials_misc import create_access_token, verify_password, get_password_hash, get_current_active_user, get_current_user, require_role


client = TestClient(app)


@pytest.fixture(scope="module")
def client_with_cleanup():
    headers = startup()
    yield client, headers
    cleanup()


def startup():
    data = {"email": "ryzeros@gmail.com"}
    token = create_access_token(data, timedelta(minutes=5))
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return headers


def cleanup():
    db = next(get_db())
    rows_del = db.query(UserModel).filter(UserModel.email == "ryzroz@gmail.com").delete()
    db.commit()


def decode_base64url(data):
    """Decode Base64 URL-encoded data."""
    padding = '=' * (4 - len(data) % 4)  # Add padding if necessary
    return base64.urlsafe_b64decode(data + padding)


def get_jwt_data(token):
    """Extract and decode the header and payload from a JWT."""
    try:
        # Split the token into its three parts
        header, payload, signature = token.split('.')

        # Decode header and payload from base64url
        header_json = decode_base64url(header)
        payload_json = decode_base64url(payload)

        # Parse the decoded strings as JSON
        header_data = json.loads(header_json)
        payload_data = json.loads(payload_json)

        return header_data, payload_data
    except (ValueError, json.JSONDecodeError, binascii.Error) as e:
        print(f"Error decoding JWT: {e}")
        return None, None


class TestLoginToken:
    def test_token_valid(self):
        data = {
            "username": "ryzeros@gmail.com",
            "password": "P@ssw0rd"
        }

        response = client.post(url="/user/token", data=data)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["access_token"]
        header, payload = get_jwt_data(response_data["access_token"])
        assert payload["email"] == "ryzeros@gmail.com"

    def test_token_invalid_password(self):
        data = {
            "username": "ryzeros@gmail.com",
            "password": "Pssw0rd"
        }

        response = client.post(url="/user/token", data=data)
        assert response.status_code == 403
        response_data = response.json()
        assert response_data["detail"] == "Forbidden"

    def test_user_credit_token(self):
        db = next(get_db())
        item = UserService(db).authenticate_user(
            email="ryzeros@gmail.com",
            password="P@ssw0rd"
        )
        assert item.status_code is None
        assert item.success
        assert item.value.access_token
        header, payload = get_jwt_data(item.value.access_token)
        assert payload["email"] == "ryzeros@gmail.com"

    def test_user_crud_token(self):
        db = next(get_db())
        item = UserCRUD(db).authenticate_user(
            email="ryzeros@gmail.com",
            password="P@ssw0rd"
        )
        assert isinstance(item, UserModel)
        assert item.email == "ryzeros@gmail.com"

    def test_verify_password(self):
        hashed_password = "$2b$12$x1o6HFZSorLgzPh5D9wY2ef0G1fBwPqsg2VDAOQ88mOtzIRvasfmW"
        hashed_password_1 = "$2b$12$8wahsIX4l9M6aNzaGoGYYeXiOMekjj1wqvAvzCfz6MtlVH25y8Vf."
        assert verify_password("P@ssw0rd", hashed_password)
        assert not verify_password("P", hashed_password)
        assert verify_password("P@ssw0rd", hashed_password_1)
        assert not verify_password("P", hashed_password_1)

    def test_create_access_token(self):
        token_1 = create_access_token({"email": "ryzeros@gmail.com"})
        header_1, payload_1 = get_jwt_data(token_1)
        assert payload_1["email"] == "ryzeros@gmail.com"
        token_2 = create_access_token({"email": "ryzroz@gmail.com"})
        header_2, payload_2 = get_jwt_data(token_2)
        assert payload_2["email"] == "ryzroz@gmail.com"


class TestCreateUser:
    def test_signup_valid(self, client_with_cleanup):
        client_with_cleanup, headers = client_with_cleanup
        data = {
            "email": "ryzroz@gmail.com",
            "password": "P@ssw0rd",
            "confirm_password": "P@ssw0rd",
            "roles": "user,partner",
            "partner_code": "ABC"
        }
        response = client_with_cleanup.post("/user/signup", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == "ryzroz@gmail.com"

    def test_signup_password_dont_match(self, client_with_cleanup):
        data = {
            "email": "ryzroz@gmail.com",
            "password": "P@ssw0rd",
            "confirm_password": "P2@ssw0rd",
            "roles": "user,partner",
            "partner_code": "ABC"
        }
        client_with_cleanup, headers = client_with_cleanup
        response = client_with_cleanup.post("/user/signup", json=data, headers=headers)
        assert response.status_code == 400
        assert response.json()["detail"]["error"] == "password and confirm password don't match"

    def test_user_service_signup(self):
        db = next(get_db())
        cleanup()
        data = UserRegisterRequest(
            email="ryzroz@gmail.com",
            password="P@ssw0rd",
            confirm_password="P@ssw0rd",
            roles="user,admin"
        )
        response = UserService(db).signup(data)
        assert response.status_code is None
        assert response.success
        assert response.value.email == "ryzroz@gmail.com"

    def test_user_crud_signup(self):
        db = next(get_db())
        cleanup()
        data = UserRegisterRequest(
            email="ryzroz@gmail.com",
            password="P@ssw0rd",
            confirm_password="P@ssw0rd",
            roles="user,admin"
        )
        response = UserCRUD(db).signup(data)
        assert isinstance(response, UserModel)
        assert response.email == "ryzroz@gmail.com"
        cleanup()
        data = UserRegisterRequest(
            email="ryzroz@gmail.com",
            password="P@ssw0rd",
            confirm_password="P@ssw0rd",
        )
        response = UserCRUD(db).signup(data)
        assert isinstance(response, UserModel)
        assert response.email == "ryzroz@gmail.com"
        assert response.roles == "user"

    def test_get_password_hash(self):
        item = get_password_hash("P@ssw0rd")
        assert verify_password("P@ssw0rd", item)
        assert not verify_password("P@sword", item)
        item_1 = get_password_hash("Password")
        assert verify_password("Password", item_1)
        assert not verify_password("Pass", item_1)


class TestGetMe:
    def test_get_me_valid(self, client_with_cleanup):
        client_with_cleanup, header = client_with_cleanup
        resp = client_with_cleanup.post("/user/me", headers=header)
        assert resp.status_code == 200
        assert resp.json()["email"] == "ryzeros@gmail.com"
        assert resp.json()["roles"] == "user,admin"
        
    def test_get_me_invalid(self, client_with_cleanup):
        client_with_cleanup, header = client_with_cleanup
        resp = client_with_cleanup.post("/user/me")
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Not authenticated"


class TestCredentialsMisc:
    @pytest.mark.asyncio
    async def test_get_current_user_valid(self):
        data = {"email": "ryzeros@gmail.com"}
        token = create_access_token(data, timedelta(minutes=5))
        user = await get_current_user(token, db=next(get_db()))
        assert user.email == "ryzeros@gmail.com"
        assert user.roles == "user,admin"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid(self):
        data = {"email": "ryzeros1@gmail.com"}
        token = create_access_token(data, timedelta(minutes=5))
        with pytest.raises(HTTPException) as exception_info:
            await get_current_user(token, db=next(get_db()))
        assert exception_info.value.status_code == 401
        assert exception_info.value.detail == "Could not validate credentials"

    @pytest.mark.asyncio
    async def test_get_current_user_expired(self):
        data = {"email": "ryzeros@gmail.com"}
        token = create_access_token(data, timedelta(seconds=1))
        time.sleep(2)
        with pytest.raises(HTTPException) as exception_info:
            await get_current_user(token, db=next(get_db()))
        assert exception_info.value.status_code == 401
        assert exception_info.value.detail == "Expired token"

    @pytest.mark.asyncio
    async def test_get_current_user_jwt_error(self):
        token = "ASDASCREGERF"
        with pytest.raises(HTTPException) as exception_info:
            await get_current_user(token, db=next(get_db()))
        assert exception_info.value.status_code == 401
        assert exception_info.value.detail == "Could not validate credentials"

    @pytest.mark.asyncio
    async def test_get_current_user_no_email(self):
        data = {"not_email": "ryzeros@gmail.com"}
        token = create_access_token(data, timedelta(seconds=1))
        with pytest.raises(HTTPException) as exception_info:
            await get_current_user(token, db=next(get_db()))
        assert exception_info.value.status_code == 401
        assert exception_info.value.detail == "Could not validate credentials"

    @pytest.mark.asyncio
    async def test_get_current_active_user_(self, client_with_cleanup):
        data = {"email": "ryzroz@gmail.com"}
        token = create_access_token(data, timedelta(seconds=1))
        user = await get_current_active_user(await get_current_user(token, next(get_db())))
        assert user.email == "ryzroz@gmail.com"

    @pytest.mark.asyncio
    async def test_get_current_active_user_disabled(self, client_with_cleanup):
        client_with_cleanup, headers = client_with_cleanup
        cleanup()
        data = {
            "email": "ryzroz@gmail.com",
            "password": "P@ssw0rd",
            "confirm_password": "P@ssw0rd",
            "roles": "user,partner",
            "partner_code": "ABC"
        }
        response = client_with_cleanup.post("/user/signup", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == "ryzroz@gmail.com"
        db = next(get_db())
        db.query(UserModel).filter(UserModel.email == "ryzroz@gmail.com").update({"disabled": True})
        db.commit()
        data = {"email": "ryzroz@gmail.com"}
        token = create_access_token(data, timedelta(seconds=1))
        with pytest.raises(HTTPException) as exception_info:
            await get_current_active_user(await get_current_user(token, next(get_db())))
        assert exception_info.value.status_code == 400
        assert exception_info.value.detail == "Inactive user"
        db.query(UserModel).filter(UserModel.email == "ryzroz@gmail.com").update({"disabled": False})
        db.commit()

    @pytest.mark.asyncio
    async def test_require_role_invalid(self, client_with_cleanup):
        data = {"email": "ryzroz@gmail.com"}
        token = create_access_token(data, timedelta(seconds=1))
        with pytest.raises(HTTPException) as exception_info:
            await require_role("admin")(await get_current_active_user(await get_current_user(token, next(get_db()))))
        assert exception_info.value.status_code == 403
        assert exception_info.value.detail == "Insufficient permissions"

    @pytest.mark.asyncio
    async def test_require_role_valid(self, client_with_cleanup):
        data = {"email": "ryzeros@gmail.com"}
        token = create_access_token(data, timedelta(seconds=1))
        user = await require_role("admin")(await get_current_active_user(await get_current_user(token, next(get_db()))))
        assert user.email == "ryzeros@gmail.com"
