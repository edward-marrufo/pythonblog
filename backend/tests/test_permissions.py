# backend/tests/test_permissions.py
import pytest
from fastapi import HTTPException
from starlette.requests import Request

from backend.app.core.permissions import require_post_owner
from backend.tests.fakes.db import FakeConnection


# ------------------------------------------------------------
# FAKE OBJECTS (we avoid real DB + real FastAPI request lifecycle)
# ------------------------------------------------------------

class FakeCursor:
    """
    Simulates a DB cursor.

    Why this exists:
    - The permission dependency calls:
        cursor = db.cursor()
        cursor.execute(...)
        cursor.fetchone()

    We fake this so we can fully control DB responses in tests.
    """

    def __init__(self, row):
        self.row = row

    def execute(self, query, params):
        # We don't actually run SQL.
        # We just store inputs if we ever want debugging visibility.
        self.query = query
        self.params = params

    def fetchone(self):
        # This simulates the DB returning either:
        # - a post row like ("user_id",)
        # - or None if post doesn't exist
        return self.row


class FakeDB:
    """
    Simulates the database object returned by get_db().

    Why this exists:
    - The dependency calls db.cursor()
    - We inject a deterministic FakeCursor instead of a real DB connection
    """

    def __init__(self, row):
        self._cursor = FakeCursor(row)

    def cursor(self):
        return self._cursor


class FakeUser:
    """
    Simulates the authenticated user returned by get_current_user.

    Why this exists:
    - The dependency checks:
        user.id
        user.role

    So we just model the minimal attributes required.
    """

    def __init__(self, user_id, role="user"):
        self.id = user_id
        self.role = role


def make_request(post_id: str):
    """
    Builds a minimal Starlette Request object.

    Why this exists:
    - The dependency reads:
        request.path_params["post_id"]

    FastAPI normally constructs this automatically.
    We simulate just enough structure for the test.
    """

    scope = {
        "type": "http",
        "path_params": {
            "post_id": post_id
        }
    }
    return Request(scope)


# ------------------------------------------------------------
# TESTS
# ------------------------------------------------------------

def test_post_owner_allowed():
    """
    CASE 1:
    User owns the post → access granted

    Logic path:
    - DB returns post with user_id = "1"
    - request user.id = "1"
    - roles don't matter (ownership matches)
    """

    request = make_request("123")

    user = FakeUser("1")
    db = FakeDB(row=("1",))  # post belongs to user "1"

    dependency = require_post_owner()

    result = dependency(
        request=request,
        user=user,
        db=db
    )
    #raise Exception("TEST REACHED")
    # If allowed, dependency returns the user unchanged
    assert result == user


def test_admin_allowed():
    """
    CASE 2:
    Admin bypasses ownership check

    Logic path:
    - DB returns post owned by user "1"
    - request user is "999"
    - BUT role = admin → always allowed
    """

    request = make_request("123")

    user = FakeUser("999", role="admin")
    db = FakeDB(row=("1",))

    dependency = require_post_owner()

    result = dependency(
        request=request,
        user=user,
        db=db
    )

    assert result == user


def test_non_owner_forbidden():
    """
    CASE 3:
    User is NOT owner and NOT admin → 403

    Logic path:
    - DB returns post owned by "1"
    - user.id = "2"
    - role = user → blocked
    """

    request = make_request("123")

    user = FakeUser("2")
    db = FakeDB(row=("1",))

    dependency = require_post_owner()

    with pytest.raises(HTTPException) as exc:
        dependency(
            request=request,
            user=user,
            db=db
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "Not authorized"


def test_post_not_found():
    """
    CASE 4:
    Post does not exist → 404

    Logic path:
    - DB returns None
    - dependency fails early before ownership check
    """

    request = make_request("123")

    user = FakeUser("1")
    db = FakeDB(row=None)

    dependency = require_post_owner()

    with pytest.raises(HTTPException) as exc:
        dependency(
            request=request,
            user=user,
            db=db
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Post not found"