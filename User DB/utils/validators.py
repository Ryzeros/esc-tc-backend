import re
from fastapi import Depends
from config.database import get_db


def validate_password(password: str):
    if password and re.match("^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,49}$", password):
        return True
    return False

def validate_email(email: str):
    if email and re.match("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return True
    return False