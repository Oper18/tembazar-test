# coding: utf-8

import os

API_HOST = os.environ.get("API_HOST", "http://127.0.0.1")

DATABASES = {
    "main": {
        "user": os.environ.get('DB_USER', 'tembazar'),
        "password": os.environ.get('DB_PASSWORD', 'tembazar'),
        "address": os.environ.get('DB_HOST', 'localhost'),
        "name": os.environ.get('DB_NAME', 'tembazar'),
        "port": os.environ.get('DB_PORT', '5432'),
    },
    "test": {
        "name": os.environ.get('DB_NAME', 'tembazar'),
    },
}

LOCAL_SALT = os.getenv('SERVER_SALT', '2b886d169a244f9cb760e6d70e3aa17c')
SERVER_SECRET = os.getenv('SERVER_SECRET', '2b886d169a244f9cb760e6d70e3aa17c')
ACCESS_TOKEN_LIFETIME = 24*60*60
REFRESH_TOKEN_LIFETIME = 24*60*60*60

try:
    TESTS = bool(int(os.environ.get("TESTS")))
except:
    TESTS = False

ACTIVE_DB = "main"
if TESTS:
    ACTIVE_DB = "test"
