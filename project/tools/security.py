import base64
import hashlib
import calendar
import datetime

import jwt
from flask import current_app, abort


def __generate_password_digest(password: str) -> bytes:
    return hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode("utf-8"),
        salt=current_app.config["PWD_HASH_SALT"],
        iterations=current_app.config["PWD_HASH_ITERATIONS"],
    )


def generate_password_hash(password: str) -> str:
    return base64.b64encode(__generate_password_digest(password)).decode('utf-8')


def compare_passwords_hash(password_hash, other_password) -> bool:
    return password_hash == generate_password_hash(other_password)


def generate_tokens(email, password, password_hash=None, is_refresh=False):
    if email is None:
        return None

    if not is_refresh:
        if not compare_passwords_hash(other_password=password, password_hash=password_hash):
            return None

    data = {
        "email": email,
        "password": password

    }

    min15 = datetime.datetime.utcnow() + datetime.timedelta(minutes=current_app.config['TOKEN_EXPIRE_MINUTES'])
    data["exp"] = calendar.timegm(min15.timetuple())
    access_token = jwt.encode(data, key=current_app.config['SECRET_KEY'], algorithm=current_app.config['ALGORITHM'])

    day130 = datetime.datetime.utcnow() + datetime.timedelta(days=current_app.config['TOKEN_EXPIRE_DAYS'])
    data["exp"] = calendar.timegm(day130.timetuple())
    refresh_token = jwt.encode(data, key=current_app.config['SECRET_KEY'],
                               algorithm=current_app.config['ALGORITHM'])

    return {"access_token": access_token, "refresh_token": refresh_token}


def approved_refresh_token(refresh_token):
    data = jwt.decode(refresh_token, key=current_app.config['SECRET_KEY'],
                      algorithms=current_app.config['ALGORITHM'])

    email = data.get("email")
    password = data.get("password")

    return generate_tokens(email, password, is_refresh=True)


def get_data_from_token(refresh_token):
    try:
        data = jwt.decode(refresh_token, key=current_app.config['SECRET_KEY'],
                          algorithms=current_app.config['ALGORITHM'])

        return data
    except Exception:
        return None
