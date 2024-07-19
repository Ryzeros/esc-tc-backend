import re
from fastapi import Depends
from config.database import get_db
from models.loyalty import LoyaltyModel


def validate_member_id(member_id: str, airline_code: str, db: get_db = Depends()):
    pattern = db.query(LoyaltyModel).filter(LoyaltyModel.program_id == airline_code).first()
    if pattern and re.match(pattern.regex_pattern, member_id):
        return True
    return False


def validate_airline_code(airline_code: str, db: get_db = Depends()):
    pattern = db.query(LoyaltyModel).filter(LoyaltyModel.program_id == airline_code).first()
    if pattern:
        return True
    return False
