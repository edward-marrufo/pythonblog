# app/routers/authentication.py
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from user_agents import parse
from datetime import datetime, timedelta
from backend.app.db import get_db
from backend.app.models.login import LoginRequest, LoginResponse
from backend.app.models.user import CurrentUser
from backend.app.core.security import hash_password, verify_password, get_current_user
from backend.app.utils.ip_utilities import get_client_ip
import secrets

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
def login_user(
    login: LoginRequest,
    request: Request,
    response: Response,
    db = Depends(get_db)):

    ip_address = get_client_ip(request)
    user_agent_string = request.headers.get("user-agent")
    client_user_agent = parse(user_agent_string)


    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT user_id, username, hashed_password FROM users WHERE username = ?", (login.username,) 
            )
            #changing from one element to storing the whole row
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            user_id = row[0]
            username = row[1]
            hashed_password = row[2]
            
            if not verify_password(login.password, hashed_password):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            session_id = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(days=7)
            
            authorization = request.headers.get("authorization")
            referer = request.headers.get("referer")
            device_name = f"{client_user_agent.browser.family} on {client_user_agent.os.family}"

            cursor.execute(
                """
                INSERT INTO sessions (session_id, user_id, device_name, user_agent, ip_address, user_agent_string, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (session_id, user_id, device_name, client_user_agent.browser.family, ip_address, user_agent_string, expires_at)
            )
            db.commit()

        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=604800
        )

        return {
            "username": row.username
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=CurrentUser)
def get_me(user: CurrentUser = Depends(get_current_user)):
    return user

@router.post("/logout")
def logout_user(
    request: Request,          # incoming request
    response: Response,        # allows us to delete cookie
    db = Depends(get_db)
):
    # Get the session_id from the client's cookie
    session_id = request.cookies.get("session_id")
    if session_id:
        # Revoke the session in the DB
        with db.cursor() as cursor:
            cursor.execute("UPDATE sessions SET revoked = TRUE WHERE session_id = ?", (session_id,))
            db.commit()
        
        # Delete the cookie from the client
        response.delete_cookie(key="session_id", path="/")

    return {"detail": "Logged out successfully"}