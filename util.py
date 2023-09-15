import hashlib

from settings import (
    LOCAL_SALT,
)


def password_hash(password, salt):
    return hashlib.sha512(password.encode("utf-8") + salt.encode("utf-8") + LOCAL_SALT.encode("utf-8")).hexdigest()
