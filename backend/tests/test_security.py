#/backend/tests/test_security.py
from backend.app.core.security import (
    PasswordHasher,
    hash_refresh_token,
    get_session,
    get_valid_session
)
from fastapi import HTTPException
# This is required for test_get_valid_session_raises_when_session_missing
from datetime import datetime, timedelta, timezone
# This is required for most tests
import pytest

# ----------------------------
# Fake DB layer (no real SQL)
# ----------------------------
""" class FakeCursor:
    def execute(self, query, params):
        self.query = query
        self.params = params

    def fetchone(self):
        return (123, "expires")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass """

class FakeCursor:
    #This stores whatever fake DB row we want the test to return
    def __init__(self, result):
        self.result = result

    #We are simulating SQL execution.
    def execute(self, query, params):
        self.query = query
        self.params = params

    #We are simulating cursor.fetchone() from a real DB
    def fetchone(self):
        return self.result
    #Python requires context manager methods when using 'with'
    #In our real code we use 'with db.cursor() as cursor:'
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

""" class FakeDB:
    def cursor(self):
        return FakeCursor() """
#Simulating our database connection object.
class FakeDB:
    def __init__(self, result):
        #Stores the fake DB result to hand to the cursor later.
        self.result = result
    #The below simuates db.cursor() from the real cursor
    def cursor(self):
        return FakeCursor(self.result)

def test_password_hash_and_verify():
    hasher = PasswordHasher()

    password = "my_secret"
    hashed = hasher.hash(password)

    result = hasher.verify(password, hashed)

    assert result is True


def test_password_verify_fails_for_wrong_password():
    hasher = PasswordHasher()

    hashed = hasher.hash("correct_password")

    result = hasher.verify("wrong_password", hashed)

    assert result is False


def test_refresh_token_is_deterministic():
    token = "abc123"

    hash1 = hash_refresh_token(token)
    hash2 = hash_refresh_token(token)

    assert hash1 == hash2


def test_refresh_token_differs_for_different_inputs():
    hash1 = hash_refresh_token("abc")
    hash2 = hash_refresh_token("xyz")

    assert hash1 != hash2

# We are only testing the responsibility of the function
# and not any downstream logic 
def test_get_session_returns_session_for_valid_session_id():
    fake_session = (123, "expires")

    result = get_session("abc123", FakeDB(fake_session))

    assert result == fake_session

# We are testing for missing session_id.
# If no 401 exception is encountered, this will fail.
def test_get_valid_session_raises_when_session_id_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_valid_session(None, FakeDB(None))

    assert exc_info.value.status_code == 401

# Testing missing db session
# If no 401 exception is encountered, this will fail.
def test_get_valid_session_raises_when_session_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_valid_session("abc123", FakeDB(None))

    assert exc_info.value.status_code == 401

# Testing for expired sessions
# If no 401 exception is encountered, this will fail.
def test_get_valid_session_raises_when_session_expired():
    expired_time = datetime.now(timezone.utc) - timedelta(days=1)

    fake_session = (123, expired_time)

    with pytest.raises(HTTPException) as exc_info:
        get_valid_session("abc123", FakeDB(fake_session))

    assert exc_info.value.status_code == 401

# Testing our happy path
def test_get_valid_session_returns_session_when_valid():
    future_time = datetime.now(timezone.utc) + timedelta(days=1)

    fake_session = (123, future_time)

    result = get_valid_session("abc123", FakeDB(fake_session))

    assert result == fake_session

# Testing tz normalization logic
def test_get_valid_session_handles_naive_datetime():
    naive_future_time = datetime.now() + timedelta(days=1)

    fake_session = (123, naive_future_time)

    result = get_valid_session("abc123", FakeDB(fake_session))

    assert result == fake_session