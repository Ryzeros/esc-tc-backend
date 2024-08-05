import datetime

from main import app
import pytest
from fastapi.testclient import TestClient
from config.database import get_db
from models.promotions import PromotionModel
from datetime import timedelta
from schemas.promotions import PromotionBase
from services.promotions import PromotionCRUD, PromotionService
from utils.credentials_misc import create_access_token
from utils.promotion_misc import eval_points_conditions

client = TestClient(app)


@pytest.fixture(scope="module")
def client_with_cleanup():
    headers = startup()
    yield client, headers
    cleanup()


def startup():
    data = {"email": "admin@dbs.com"}
    token = create_access_token(data, timedelta(minutes=5))
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return headers


def cleanup():
    db = next(get_db())
    rows_del = db.query(PromotionModel).filter(PromotionModel.partner_code == "TEST").delete()
    db.commit()


class TestGetPromotionsByPartner:
    def test_get_all_promotions_valid(self, client_with_cleanup):
        client_with_cleanup, header = client_with_cleanup
        resp = client.post(url="/promotions/get_by_partner_id/", headers=header)
        assert resp.status_code == 200
        response_data = resp.json()
        assert len(response_data) == 2

    def test_get_all_promotions_invalid(self, client_with_cleanup):
        resp = client.post(url="/promotions/get_by_partner_id/")
        assert resp.status_code == 401

    def test_get_all_promotions_no_role(self):
        data = {"email": "ryzeros@gmail.com"}
        token = create_access_token(data, timedelta(minutes=5))
        headers = {
            "Authorization": f"Bearer {token}"
        }
        resp = client.post(url="/promotions/get_by_partner_id/", headers=headers)
        assert resp.status_code == 403

    def test_promotion_service(self):
        db = next(get_db())
        resp = PromotionService(db).get_all_promotions_partner("DBS")
        assert resp.status_code is None
        assert resp.success
        assert isinstance(resp.value, list)

        resp = PromotionService(db).get_all_promotions_partner("DONT EXIST")
        assert resp.status_code == 404

    def test_promotion_crud(self):
        db = next(get_db())
        resp = PromotionCRUD(db).get_all_promotions_partner("DBS")
        assert isinstance(resp, list)
        assert resp[0].partner_code == "DBS"

        resp = PromotionCRUD(db).get_all_promotions_partner("DONT EXIST")
        assert resp is None


class TestGetPromotionById:
    def test_get_by_id_valid(self, client_with_cleanup):
        client_with_cleanup, header = client_with_cleanup
        data = {
            "id": 8
        }
        resp = client.post(url="/promotions/get_by_id/", headers=header, json=data)
        assert resp.status_code == 200
        response_data = resp.json()
        assert response_data["id"] == 8

    def test_get_by_id_invalid(self, client_with_cleanup):
        client_with_cleanup, header = client_with_cleanup
        data = {
            "id": 100000
        }
        resp = client.post(url="/promotions/get_by_id/", headers=header, json=data)
        assert resp.status_code == 404

    def test_promotion_service_get_by_id(self):
        db = next(get_db())
        resp = PromotionService(db).get_promotion_by_id(8)
        assert resp.status_code is None
        assert resp.success
        assert resp.value.partner_code == "DBS"

        resp = PromotionService(db).get_promotion_by_id(10000)
        assert resp.status_code == 404

    def test_promotion_crud_get_by_id(self):
        db = next(get_db())
        resp = PromotionCRUD(db).get_promotion_by_id(8)
        assert isinstance(resp, PromotionModel)
        assert resp.partner_code == "DBS"

        resp = PromotionCRUD(db).get_promotion_by_id(10000)
        assert resp is None


class TestGetNameDescription:
    def test_get_name_description(self, client_with_cleanup):
        client_with_cleanup, header = client_with_cleanup
        resp = client.post(url="/promotions/get_name_description/", headers=header)
        assert resp.status_code == 200
        response_data = resp.json()
        assert len(response_data) == 2
        assert response_data[0]["name"]

    def test_get_name_description_invalid(self, client_with_cleanup):
        resp = client.post(url="/promotions/get_name_description/")
        assert resp.status_code == 401

    def test_promotion_service_get_name_description(self):
        db = next(get_db())
        resp = PromotionService(db).get_all_promotion_names("DBS")
        assert resp.status_code is None
        assert resp.success
        assert isinstance(resp.value, list)

        resp = PromotionService(db).get_all_promotion_names("DONT EXIST")
        assert resp.status_code == 404

    def test_promotion_crud_get_name_description(self):
        db = next(get_db())
        resp = PromotionCRUD(db).get_all_promotion_names("DBS")
        assert isinstance(resp, list)
        assert resp[0].name

        resp = PromotionCRUD(db).get_all_promotion_names("DONT EXIST")
        assert resp is None


class TestAddPromotions:
    def test_add_promotion_valid(self, client_with_cleanup):
        token_data = {
            "email": "ryzeros@gmail.com"
        }
        data = {
            "name": "1.5 times more exchange rate",
            "description": "Get 1.5 times more miles when you spend more than $1000 on a card in a year.",
            "airline_code": "GJP",
            "partner_code": "TEST",
            "expiry": (datetime.datetime.now() + timedelta(days=30)).isoformat(),
            "points_rule": {"point_condition": [["x > 1500", "x * 1.5"]]},
            "conditions": {"TUG Max": {"op": "gt", "value": "1000"}},
            "start_date_for_card": datetime.datetime(2024, 1, 1, 0, 0, 0).isoformat(),
            "end_date_for_card": datetime.datetime(2024, 12, 31, 23, 59, 59).isoformat()
        }
        client_with_cleanup, _ = client_with_cleanup
        token = create_access_token(token_data, timedelta(minutes=5))
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = client.post("/promotions/add", json=data, headers=headers)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["airline_code"] == "GJP"
        assert response_data["partner_code"] == "TEST"

    def test_promotion_service_add_item(self):
        item = PromotionBase(
            name="1.5 times more exchange rate",
            description="Get 1.5 times more miles when you spend more than $1000 on a card in a year.",
            airline_code="GJP",
            partner_code="TEST",
            expiry=(datetime.datetime.now() + timedelta(days=30)).isoformat(),
            points_rule={"point_condition": [["x > 1500", "x * 1.5"]]},
            conditions={"TUG Max": {"op": "gt", "value": "1000"}},
            start_date_for_card=datetime.datetime(2024, 1, 1, 0, 0, 0).isoformat(),
            end_date_for_card=datetime.datetime(2024, 12, 31, 23, 59, 59).isoformat()
        )
        db = next(get_db())
        resp = PromotionService(db).add_item(item)
        assert resp.status_code is None
        assert resp.success
        assert resp.value.airline_code == "GJP"
        assert resp.value.partner_code == "TEST"

    def test_promotion_crud_add_item(self):
        item = PromotionBase(
            name="1.5 times more exchange rate",
            description="Get 1.5 times more miles when you spend more than $1000 on a card in a year.",
            airline_code="GJP",
            partner_code="TEST",
            expiry=(datetime.datetime.now() + timedelta(days=30)).isoformat(),
            points_rule={"point_condition": [["x > 1500", "x * 1.5"]]},
            conditions={"TUG Max": {"op": "gt", "value": "1000"}},
            start_date_for_card=datetime.datetime(2024, 1, 1, 0, 0, 0).isoformat(),
            end_date_for_card=datetime.datetime(2024, 12, 31, 23, 59, 59).isoformat()
        )
        db = next(get_db())
        resp = PromotionCRUD(db).add_items(item)
        assert resp.airline_code == "GJP"
        assert resp.partner_code == "TEST"


class TestGetAirlinePartnerPromotions:
    def test_get_airline_promotions(self):
        db = next(get_db())
        item = PromotionCRUD(db).get_airline_partner_promotions("GJP", "DBS")
        assert isinstance(item, list)
        assert isinstance(item[0], PromotionModel)

    def test_get_airline_promotions_invalid(self):
        db = next(get_db())
        item = PromotionCRUD(db).get_airline_partner_promotions("NOT EXIST", "DBS")
        assert item is None


class TestPromotionsMisc:
    def test_eval_points_conditions(self):
        assert eval_points_conditions("600 < x < 1000", 700)
        assert not eval_points_conditions("600 < x < 1000", 100)
        assert eval_points_conditions("600 <= x <= 1000", 600)
        assert eval_points_conditions("600 <= x <= 1000", 1000)
        assert not eval_points_conditions("600 <= x < 1000", 1000)
        assert not eval_points_conditions("600 < x <= 1000", 600)

        assert eval_points_conditions("x < 1000", 999)
        assert eval_points_conditions("x <= 1000", 1000)
        assert eval_points_conditions("x > 600", 700)
        assert eval_points_conditions("x >= 600", 600)
        assert eval_points_conditions("x == 600", 600)
        assert eval_points_conditions("x != 600", 601)

        with pytest.raises(ValueError) as excinfo:
            eval_points_conditions("600 ! x < 1000", 500)
        assert str(excinfo.value) == "Invalid condition format: 600 ! x < 1000"

        with pytest.raises(ValueError) as excinfo:
            eval_points_conditions("600 < x ! 1000", 700)
        assert str(excinfo.value) == "Invalid condition format: 600 < x ! 1000"

        assert eval_points_conditions("600 > x < 1000", 500)
        assert eval_points_conditions("600 > x > 400", 500)
        assert eval_points_conditions("600 > x >= 400", 400)
        assert eval_points_conditions("600 >= x < 1000", 600)
        assert not eval_points_conditions("600 >= x > 400", 400)
        assert eval_points_conditions("600 >= x >= 400", 600)

        assert eval_points_conditions("x > 1000", 1001)
        assert eval_points_conditions("x >= 1000", 1000)
        assert not eval_points_conditions("x > 1000", 1000)
        assert not eval_points_conditions("x >= 1000", 999)
