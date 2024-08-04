import pytest
from main import app
import base64
import json
from datetime import timedelta
from config.database import get_db
from fastapi.testclient import TestClient
from models.user import UserModel
from utils.credentials_misc import create_access_token
import binascii
from fastapi.security import OAuth2PasswordRequestForm
from services.user import UserService, UserCRUD
from utils.credentials_misc import verify_password, create_access_token



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

