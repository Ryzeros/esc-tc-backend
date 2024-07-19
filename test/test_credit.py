import pytest
from fastapi.testclient import TestClient
from main import app
from config.database import get_db
from services.credit import CreditService, CreditCRUD
from schemas.credit import CreditCreate
from models.credit import CreditModel
from utils.promotion_misc import validate_promotions, eval_points_conditions, calculate_points
from utils.validators import validate_airline_code, validate_member_id

client = TestClient(app)


@pytest.fixture(scope="module")
def client_with_cleanup():
    yield client
    cleanup()


def cleanup():
    data = {
        "email": "ryzeros@gmail.com",
        "partner_code": "DBS"
    }
    data_2 = {
        "email": "ryzeros@gmail.com",
        "partner_code": "OCBC"
    }
    client.post("/credit/delete", params=data)
    client.post("/credit/delete", params=data_2)


def test_add_credit_no_promotions(client_with_cleanup):
    data = {
        "member_id": "1234567890",
        "amount": 100,
        "first_name": "You Xiang",
        "last_name": "Teo",
        "airline_code": "GJP",
        "partner_code": "OCBC",
        "email": "ryzeros@gmail.com",
        "additional_info": {}
    }

    response = client_with_cleanup.post("/credit/add/", json=data)
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
    data.pop("partner_code")
    data["status"] = response_data["status"]

    assert data == response_data


def test_add_credit_invalid_member_id(client_with_cleanup):
    data = {
        "member_id": "15",
        "amount": 100,
        "first_name": "You Xiang",
        "last_name": "Teo",
        "airline_code": "GJP",
        "partner_code": "OCBC",
        "email": "ryzeros@gmail.com",
        "additional_info": {}
    }
    response = client_with_cleanup.post("/credit/add/", json=data)
    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "error": "invalid member ID"
        }
    }


def test_add_credit_invalid_airline_code(client_with_cleanup):
    data = {
        "member_id": "1234567890",
        "amount": 100,
        "first_name": "You Xiang",
        "last_name": "Teo",
        "airline_code": "NON",
        "partner_code": "OCBC",
        "email": "ryzeros@gmail.com",
        "additional_info": {}
    }
    response = client_with_cleanup.post("/credit/add/", json=data)
    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "error": "invalid airline code"
        }
    }


def test_add_credit_with_promotions(client_with_cleanup):
    data = {
        "member_id": "1234567890",
        "amount": 100,
        "first_name": "You Xiang",
        "last_name": "Teo",
        "airline_code": "GJP",
        "partner_code": "DBS",
        "email": "ryzeros@gmail.com",
        "additional_info": {
            "black_card_holder": "true",
            "monthly_spending": 2000
        }
    }

    response = client_with_cleanup.post("/credit/add/", json=data)
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
    data.pop("partner_code")
    data["amount"] = response_data["amount"]
    data["status"] = response_data["status"]

    assert data == response_data


def test_credit_service_add_item():
    db = next(get_db())
    item = CreditCreate(
        member_id="1234567890",
        amount=100,
        first_name="You Xiang",
        last_name="Teo",
        airline_code="GJP",
        partner_code="DBS",
        email="ryzeros@gmail.com",
        additional_info={}

    )
    item = CreditService(db).add_item(item)
    assert item.status_code is None
    assert item.success
    assert item.exception_case is None
    assert isinstance(item.value, CreditModel)
    assert item.value.member_id == "1234567890"
    assert item.value.status == "In Progress"


def test_credit_crud_add_item():
    db = next(get_db())
    item = CreditCreate(
        member_id="1234567890",
        amount=100,
        first_name="You Xiang",
        last_name="Teo",
        airline_code="GJP",
        partner_code="DBS",
        email="ryzeros@gmail.com",
        additional_info={}

    )
    item = CreditCRUD(db).add_item(item)
    assert isinstance(item, CreditModel)
    assert item.member_id == "1234567890"
    assert item.status == "In Progress"


def test_validate_airline_code():
    db = next(get_db())
    assert validate_airline_code("GJP", db)
    assert not validate_airline_code("NON", db)


def test_validate_member_id():
    db = next(get_db())
    assert validate_member_id("1234567890", "GJP", db)
    assert validate_member_id("1234567890123456", "GJP", db)
    assert not validate_member_id("123456", "GJP", db)


def test_validate_promotions():
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


def test_eval_points_conditions():
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


def test_calculate_points():
    formula = "x + 600"
    formula_two = "(1.5 * x) + 200"
    formula_three = "1.5 * x"

    assert calculate_points(1000, formula) == 1600
    assert calculate_points(1000, formula_two) == 1700
    assert calculate_points(1000, formula_three) == 1500
