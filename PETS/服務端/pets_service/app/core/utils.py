# -*- coding: utf-8 -*-

import string
import secrets
from jose import jwt
from sanitize_filename import sanitize
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.core.schemas import Result
from app.core.config import settings


def _result_wrapper(result: Result, status_code: int = 400):
    json_result = jsonable_encoder(result)
    return JSONResponse(status_code=status_code, content=json_result)


def decode_jwt_token(token):
    JWT_SECRET_KEY = settings.JWT_SECRET_KEY
    try:
        decode_info = jwt.decode(token, JWT_SECRET_KEY)
    except Exception as e:
        return False, str(e)
    return True, decode_info


def gen_default_password():
    length = 12
    alphabet = string.ascii_letters + string.digits + sanitize(string.punctuation)
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password


def check_string_length(item):
    item = str(item)
    if 8 <= len(item) <= 12:
        return True
    return False


def check_string_has_digit(item):
    item = str(item)
    for i in item:
        if i.isdigit():
            return True
    return False


def check_string_has_uppercase(item):
    item = str(item)
    for i in item:
        if i.isupper():
            return True
    return False


def check_password_rule(password):
    if not check_string_length(password):
        return False, 'password length is not 8 to 12 character long'

    if not check_string_has_digit(password):
        return False, 'password does not contain any digit'

    if not check_string_has_uppercase(password):
        return False, 'password does not contain any uppercase letter'
    return True, 'password is ok'
