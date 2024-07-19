import pytest
from fastapi.testclient import TestClient
from main import app

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
