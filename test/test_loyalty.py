import pytest
from main import app
from datetime import timedelta
from config.database import get_db
from models.loyalty import LoyaltyModel
from fastapi.testclient import TestClient
from schemas.loyalty import LoyaltyValidate, LoyaltyItem
from utils.credentials_misc import create_access_token
from services.loyalty import LoyaltyService, LoyaltyCRUD


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
    rows_del = db.query(LoyaltyModel).filter(LoyaltyModel.program_id == "TEST").delete()
    db.commit()


class TestAddLoyalty:
    def test_add_loyalty_valid(self, client_with_cleanup):
        data = {
            "program_id": "TEST",
            "program_name": "TESTING",
            "currency_name": "TST",
            "processing_time": "10 days",
            "description": "TESTING 123",
            "enrollment_link": "enroll.com",
            "terms_link": "enroll.com",
            "regex_pattern": r"\d{5}"
        }
        client_with_cleanup, headers = client_with_cleanup
        response = client_with_cleanup.post(url="/loyalty/add/", json=data, headers=headers)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["program_id"] == data["program_id"]

    def test_add_loyalty_invalid(self, client_with_cleanup):
        data = {
            "program_id": "TEST",
            "program_name": "TESTING",
            "currency_name": "TST",
            "processing_time": "10 days",
            "description": "TESTING 123",
            "enrollment_link": "enroll.com",
            "terms_link": "enroll.com",
            "regex_pattern": r"^\d+("
        }
        client_with_cleanup, headers = client_with_cleanup
        cleanup()
        response = client_with_cleanup.post(url="/loyalty/add/", json=data, headers=headers)
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["detail"]["message"] == "Regex Pattern invalid"

    def test_add_loyalty_exist(self, client_with_cleanup):
        data = {
            "program_id": "TEST",
            "program_name": "TESTING",
            "currency_name": "TST",
            "processing_time": "10 days",
            "description": "TESTING 123",
            "enrollment_link": "enroll.com",
            "terms_link": "enroll.com",
            "regex_pattern": r"^\d+"
        }
        client_with_cleanup, headers = client_with_cleanup
        client_with_cleanup.post(url="/loyalty/add/", json=data, headers=headers)
        response = client_with_cleanup.post(url="/loyalty/add/", json=data, headers=headers)
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["detail"]["message"] == "Program ID exists"

    def test_loyalty_service_add(self):
        db = next(get_db())
        cleanup()
        item = LoyaltyValidate(
            program_id="TEST",
            program_name="TESTING",
            currency_name="TST",
            processing_time="10 days",
            description="TESTING 123",
            enrollment_link="enroll.com",
            terms_link="enroll.com",
            regex_pattern=r"^\d+"
        )
        resp = LoyaltyService(db).add_item(item)
        assert resp.status_code is None
        assert resp.success
        assert resp.value.program_id == "TEST"

    def test_loyalty_crud_add(self):
        db = next(get_db())
        cleanup()
        item = LoyaltyValidate(
            program_id="TEST",
            program_name="TESTING",
            currency_name="TST",
            processing_time="10 days",
            description="TESTING 123",
            enrollment_link="enroll.com",
            terms_link="enroll.com",
            regex_pattern=r"^\d+"
        )
        resp = LoyaltyCRUD(db).add_item(item)
        assert resp.program_id == "TEST"


class TestGetLoyalty:
    def test_get_loyalty(self, client_with_cleanup):
        response = client.get(url="/loyalty/")
        assert response.status_code == 200
        response_data = response.json()
        items = ["program_id", "program_name", "currency_name", "processing_time", "description", "enrollment_link",
                 "terms_link"]
        assert isinstance(response_data, list)
        assert list(response_data[0].keys()) == items

    def test_loyalty_service_get(self):
        db = next(get_db())
        items = LoyaltyService(db).get_all()
        assert items.status_code is None
        assert items.success
        assert isinstance(items.value, list)
        assert isinstance(items.value[0], LoyaltyModel)

    def test_loyalty_crud_get(self):
        db = next(get_db())
        items = LoyaltyCRUD(db).get_all()
        assert isinstance(items, list)
        assert isinstance(items[0], LoyaltyModel)
