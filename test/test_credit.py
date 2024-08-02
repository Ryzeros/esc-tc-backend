import pytest
from fastapi.testclient import TestClient
from main import app
from datetime import timedelta
from config.database import get_db
from services.credit import CreditService, CreditCRUD
from schemas.credit import CreditCreate, CreditMember, CreditReference, CreditEmail
from models.credit import CreditModel
from utils.promotion_misc import validate_promotions, eval_points_conditions, calculate_points
from utils.validators import validate_airline_code, validate_member_id
from utils.credentials_misc import create_access_token

client = TestClient(app)


@pytest.fixture(scope="module")
def client_with_cleanup():
    headers = startup()
    yield client, headers
    cleanup(headers)


def startup():
    data = {"email": "admin@dbs.com"}
    token = create_access_token(data, timedelta(minutes=5))
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return headers


def cleanup(headers):
    data = {
        "email": "ryzeros@gmail.com",
    }
    client.post("/credit/delete_by_email/", json=data, headers=headers)


def add_data(client_, headers):
    input_data = {
        "member_id": "0987654321",
        "amount": 100,
        "first_name": "You Xiang",
        "last_name": "Teo",
        "airline_code": "GJP",
        "email": "ryzeros@gmail.com",
        "additional_info": {}
    }
    add_response = client_.post("/credit/add/", json=input_data, headers=headers)
    assert add_response.status_code == 200

    return add_response


class TestGetByEmailAirlineCode:
    def test_get_by_member_id_valid(self, client_with_cleanup):
        data = {
            "member_id": "0987654321",
            "airline_code": "GJP"
        }
        client_with_cleanup, headers = client_with_cleanup
        add_response = add_data(client_with_cleanup, headers)

        response = client_with_cleanup.post("/credit/get_by_member_id/", json=data, headers=headers)
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 1
        assert response_data[0]['reference'] == add_response.json()['reference']

    def test_get_by_member_id_invalid_airline(self, client_with_cleanup):
        data = {
            "member_id": "0987654321",
            "airline_code": "ASD"
        }
        client_with_cleanup, headers = client_with_cleanup

        response = client_with_cleanup.post("/credit/get_by_member_id/", json=data, headers=headers)
        assert response.status_code == 404

    def test_get_by_member_id_no_item(self, client_with_cleanup):
        data = {
            "email": "ryzeros@gmail.com",
        }
        client_with_cleanup, headers = client_with_cleanup
        client.post("/credit/delete_by_email/", json=data, headers=headers)
        data = {
            "member_id": "0987654321",
            "airline_code": "GJP"
        }

        response = client_with_cleanup.post("/credit/get_by_member_id/", json=data, headers=headers)
        assert response.status_code == 404

    def test_credit_service_get_by_member_id(self, client_with_cleanup):
        db = next(get_db())
        client_with_cleanup, headers = client_with_cleanup
        add_response = add_data(client_with_cleanup, headers)

        item = CreditMember(
            member_id="0987654321",
            airline_code="GJP"
        )
        item.set_partner_code("DBS")
        item = CreditService(db).get_by_member_id(item)
        assert item.status_code is None
        assert item.success
        assert item.exception_case is None
        assert isinstance(item.value, list)
        assert len(item.value) == 1
        assert str(item.value[0].reference) == add_response.json()["reference"]

    def test_credit_crud_get_by_member_id(self, client_with_cleanup):
        db = next(get_db())
        client_with_cleanup, headers = client_with_cleanup
        cleanup(headers)
        add_response = add_data(client_with_cleanup, headers)
        assert add_response.status_code == 200
        item = CreditMember(
            member_id="0987654321",
            airline_code="GJP"
        )
        item.set_partner_code("DBS")
        item = CreditCRUD(db).get_by_member_id(item)
        assert len(item) == 1
        assert str(item[0].reference) == add_response.json()["reference"]


class TestAddCredit:
    def test_add_credit_no_promotions(self, client_with_cleanup):
        data = {
            "member_id": "1234567890",
            "amount": 100,
            "first_name": "You Xiang",
            "last_name": "Teo",
            "airline_code": "GJP",
            "email": "ryzeros@gmail.com",
            "additional_info": {}
        }
        client_with_cleanup, headers = client_with_cleanup
        response = client_with_cleanup.post("/credit/add/", json=data, headers=headers)
        assert response.status_code == 200
        response_data = response.json()
        assert "reference" in response_data
        assert "transaction_date" in response_data
        assert response_data["status"] == "In Progress"
        assert response_data["amount"] == 100
        data["reference"] = response_data["reference"]
        data["transaction_date"] = response_data["transaction_date"]
        data.pop("additional_info")
        data.pop("email")
        data["status"] = response_data["status"]

        assert data == response_data

    def test_add_credit_invalid_member_id(self, client_with_cleanup):
        data = {
            "member_id": "15",
            "amount": 100,
            "first_name": "You Xiang",
            "last_name": "Teo",
            "airline_code": "GJP",
            "email": "ryzeros@gmail.com",
            "additional_info": {}
        }
        client_with_cleanup, headers = client_with_cleanup
        response = client_with_cleanup.post("/credit/add/", json=data, headers=headers)
        assert response.status_code == 400
        assert response.json() == {
            "detail": {
                "error": "invalid member ID"
            }
        }

    def test_add_credit_invalid_airline_code(self, client_with_cleanup):
        data = {
            "member_id": "1234567890",
            "amount": 100,
            "first_name": "You Xiang",
            "last_name": "Teo",
            "airline_code": "NON",
            "email": "ryzeros@gmail.com",
            "additional_info": {}
        }
        client_with_cleanup, headers = client_with_cleanup
        response = client_with_cleanup.post("/credit/add/", json=data, headers=headers)
        assert response.status_code == 400
        assert response.json() == {
            "detail": {
                "error": "invalid airline code"
            }
        }

    def test_add_credit_with_promotions(self, client_with_cleanup):
        data = {
            "member_id": "1234567890",
            "amount": 100,
            "first_name": "You Xiang",
            "last_name": "Teo",
            "airline_code": "GJP",
            "email": "ryzeros@gmail.com",
            "additional_info": {
                "black_card_holder": "true",
                "monthly_spending": 2000
            }
        }
        client_with_cleanup, headers = client_with_cleanup
        response = client_with_cleanup.post("/credit/add/", json=data, headers=headers)
        assert response.status_code == 200
        response_data = response.json()
        assert "reference" in response_data
        assert "transaction_date" in response_data
        assert response_data["status"] == "In Progress"
        assert response_data["amount"] == 700
        data["reference"] = response_data["reference"]
        data["transaction_date"] = response_data["transaction_date"]
        data.pop("additional_info")
        data.pop("email")
        data["amount"] = response_data["amount"]
        data["status"] = response_data["status"]

        assert data == response_data

    def test_credit_service_add_item(self):
        db = next(get_db())
        item = CreditCreate(
            member_id="1234567890",
            amount=100,
            first_name="You Xiang",
            last_name="Teo",
            airline_code="GJP",
            email="ryzeros@gmail.com",
            additional_info={}

        )
        item.set_partner_code("DBS")
        item = CreditService(db).add_item(item)
        assert item.status_code is None
        assert item.success
        assert item.exception_case is None
        assert isinstance(item.value, CreditModel)
        assert item.value.member_id == "1234567890"
        assert item.value.status == "In Progress"

    def test_credit_crud_add_item(self):
        db = next(get_db())
        item = CreditCreate(
            member_id="1234567890",
            amount=100,
            first_name="You Xiang",
            last_name="Teo",
            airline_code="GJP",
            email="ryzeros@gmail.com",
            additional_info={}

        )
        item.set_partner_code("DBS")

        item = CreditCRUD(db).add_item(item)
        assert isinstance(item, CreditModel)
        assert item.member_id == "1234567890"
        assert item.status == "In Progress"

    def test_validate_airline_code(self):
        db = next(get_db())
        assert validate_airline_code("GJP", db)
        assert not validate_airline_code("NON", db)

    def test_validate_member_id(self):
        db = next(get_db())
        assert validate_member_id("1234567890", "GJP", db)
        assert validate_member_id("1234567890123456", "GJP", db)
        assert not validate_member_id("123456", "GJP", db)

    def test_validate_promotions(self):
        rule = {
            "monthly_spending": {"op": "gt", "value": 1500},
            "black_card_holder": {"op": "eq", "value": "true"}
        }

        valid_data = {
            "monthly_spending": 2000,
            "black_card_holder": "true"
        }

        invalid_data = {
            "monthly_spending": 1000,
            "black_card_holder": "true"
        }

        assert validate_promotions(rule, valid_data)
        assert not validate_promotions(rule, invalid_data)

    def test_eval_points_conditions(self):
        condition = "600 < x < 1000"
        condition_two = "x > 6000"
        condition_three = "600 < x <= 1000"

        assert eval_points_conditions(condition, 700)
        assert not eval_points_conditions(condition, 100)
        assert not eval_points_conditions(condition, 1000)

        assert eval_points_conditions(condition_two, 6100)
        assert not eval_points_conditions(condition_two, 5000)

        assert eval_points_conditions(condition_three, 610)
        assert eval_points_conditions(condition_three, 1000)
        assert not eval_points_conditions(condition_three, 600)
        assert not eval_points_conditions(condition_three, 1001)

    def test_calculate_points(self):
        formula = "x + 600"
        formula_two = "(1.5 * x) + 200"
        formula_three = "1.5 * x"

        assert calculate_points(1000, formula) == 1600
        assert calculate_points(1000, formula_two) == 1700
        assert calculate_points(1000, formula_three) == 1500


class TestGetByReference:
    def test_get_by_reference_valid(self, client_with_cleanup):
        client_with_cleanup, headers = client_with_cleanup
        add_response = add_data(client_with_cleanup, headers)

        data = {
            "reference": f"{add_response.json()['reference']}",
        }
        response = client_with_cleanup.post("/credit/get_by_reference/", json=data, headers=headers)
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert response_data['reference'] == add_response.json()['reference']

    def test_get_by_reference_no_item(self, client_with_cleanup):
        data = {
            "reference": f"b47bfecb-32b1-46ea-ddad-27edc30f8af1",
        }
        client_with_cleanup, headers = client_with_cleanup

        response = client_with_cleanup.post("/credit/get_by_reference/", json=data, headers=headers)
        assert response.status_code == 404

    def test_get_by_reference_invalid_reference(self, client_with_cleanup):
        data = {
            "reference": f"b47bfecb-32b1-46ea-da-27edc30f8af1",
        }
        client_with_cleanup, headers = client_with_cleanup

        response = client_with_cleanup.post("/credit/get_by_reference/", json=data, headers=headers)
        assert response.status_code == 404

    def test_credit_service_get_by_reference(self, client_with_cleanup):
        db = next(get_db())
        client_with_cleanup, headers = client_with_cleanup
        add_response = add_data(client_with_cleanup, headers)

        item = CreditReference(
            reference=f"{add_response.json()['reference']}"
        )
        item.set_partner_code("DBS")
        item = CreditService(db).get_item_by_reference(reference=item)
        assert item.status_code is None
        assert item.success
        assert item.exception_case is None
        assert str(item.value.reference) == add_response.json()["reference"]

    def test_credit_crud_get_by_reference(self, client_with_cleanup):
        db = next(get_db())
        client_with_cleanup, headers = client_with_cleanup
        add_response = add_data(client_with_cleanup, headers)

        item = CreditReference(
            reference=f"{add_response.json()['reference']}"
        )
        item.set_partner_code("DBS")
        item = CreditCRUD(db).get_item_by_reference(reference=item)
        assert str(item.reference) == add_response.json()["reference"]


class TestGetByEmail:

    def test_get_by_email_valid(self, client_with_cleanup):
        client_with_cleanup, headers = client_with_cleanup
        cleanup(headers)
        add_response = add_data(client_with_cleanup, headers)
        data = {
            "email": "ryzeros@gmail.com",
        }
        response = client_with_cleanup.post("/credit/get_by_email/", json=data, headers=headers)
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 1
        assert response_data[0]['reference'] == add_response.json()['reference']

    def test_get_by_email_invalid(self, client_with_cleanup):
        client_with_cleanup, headers = client_with_cleanup
        data = {
            "email": 12345678,
        }
        response = client_with_cleanup.post("/credit/get_by_email/", json=data, headers=headers)
        assert response.status_code == 422

    def test_get_by_email_no_item(self, client_with_cleanup):
        client_with_cleanup, headers = client_with_cleanup
        cleanup(headers)
        data = {
            "email": "ryzeros@gmail.com",
        }
        response = client_with_cleanup.post("/credit/get_by_email/", json=data, headers=headers)
        assert response.status_code == 404

    def test_credit_service_get_by_email(self, client_with_cleanup):
        db = next(get_db())
        client_with_cleanup, headers = client_with_cleanup
        add_response = add_data(client_with_cleanup, headers)
        item = CreditEmail(
            email="ryzeros@gmail.com"
        )
        item.set_partner_code("DBS")
        item = CreditService(db).get_items_by_email(item)
        assert item.status_code is None
        assert item.success
        assert item.exception_case is None
        assert isinstance(item.value, list)
        assert len(item.value) == 1
        assert str(item.value[0].reference) == add_response.json()["reference"]

    def test_credit_crud_get_by_email(self, client_with_cleanup):
        db = next(get_db())
        client_with_cleanup, headers = client_with_cleanup
        cleanup(headers)
        add_response = add_data(client_with_cleanup, headers)
        assert add_response.status_code == 200
        item = CreditEmail(
            email="ryzeros@gmail.com"
        )
        item.set_partner_code("DBS")
        item = CreditCRUD(db).get_items_by_email(item)
        assert len(item) == 1
        assert str(item[0].reference) == add_response.json()["reference"]
