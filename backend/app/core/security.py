#/backend/app/core/security.py
from fastapi import Request, HTTPException, Depends
from datetime import datetime, timezone
from passlib.context import CryptContext
from backend.app.models.user import CurrentUser
from backend.app.db import get_db
import hashlib

##pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


##Password logic
class PasswordHasher:
    def __init__(self):
        self._ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str):
        return self._ctx.hash(password)
        
    def verify(self, password: str, hashed: str):
        return self._ctx.verify(password, hashed)

# Create a single instance (this replaces pwd_context)
pwd_context = PasswordHasher()

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

def hash_refresh_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()


##Database access layer

def get_session(session_id: str, db):
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT user_id, expires_at
            FROM sessions
            WHERE session_id = ? AND revoked = FALSE
        """, (session_id,))
        return cursor.fetchone()

def get_user_by_id(user_id, db):
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT user_id, username, role
            FROM users
            WHERE user_id = ?
        """, (user_id,))
        return cursor.fetchone()



## auth layer
## this is not unit testable due to it being integration level
def get_current_user(request: Request, db = Depends(get_db)):
    # Access the cookie and then validate our session
    session_id = request.cookies.get("session_id")
    session = get_valid_session(session_id, db)
    #Below, we only care about the user_id. I will leave the session context
    #for now just in case we decide to implement some other functions later
    user_id, _ = session

    # Queries db to get full user object
    # Then we validate existence of the user
    user = get_user_by_id(user_id, db)
    validate_user_exists(user)
    return CurrentUser(
    id=str(user.user_id),
    username=user.username,
    role=user.role
)

def get_valid_session(session_id: str, db):
    # Validating the session_id
    # if session_id doesn't exist, return unauthorized but in reality they are not authenticated
    if not session_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Access the session and then validate the session exists
    session = get_session(session_id, db)
    # If the session itself doesn't exist, return unauthorized but in reality this is an invalid session
    if not session:
        raise HTTPException(401, "Unauthorized")

    # Unpacking the user_id and expires_at values from the session tuple above
    # user_id is no longer needed so we only care about expires_at
    _, expires_at = session

    # If TZ doesn't exist for the expiration time then we assign UTC
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    # Validating the session expiration
    # Compares expiration time with current time, if expired, the req is rejected
    # return unauthorized but in reality the session is expired
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(401, "Unauthorized")
    return session

def validate_user_exists(user):
    # If user doesn't exist, req is rejected. This prevents orphaned sessions from being used.
    # Returns not authenticated, but in reality the user is not found.
    if not user:
        raise HTTPException(401, "Unauthorized")