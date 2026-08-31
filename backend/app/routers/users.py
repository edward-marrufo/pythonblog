# backend/app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException
from backend.app.db import get_db
from backend.app.models.user import UserRegister, User
from backend.app.core.security import hash_password

router = APIRouter(prefix="/auth", tags=["register"])


@router.post("/register", response_model=User)
def create_user(user: UserRegister, db=Depends(get_db)):
    try:
        with db.cursor() as cursor:

            # Insert user (no RETURNING with ODBC-safe approach)
            cursor.execute(
                "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
                (user.username, user.email, hash_password(user.password))
            )

            db.commit()

            # Fetch inserted user explicitly (reliable with pyodbc)
            cursor.execute(
                "SELECT username, created_at FROM users WHERE email = ?",
                (user.email,)
            )

            row = cursor.fetchone()

        if not row:
            raise HTTPException(
                status_code=500,
                detail="User was inserted but could not be retrieved"
            )

        return User(
            username=row.username,
            created_at=row.created_at
        )

    except Exception as e:
        db.rollback()
        print("FULL DB ERROR:", repr(e))  # ADD THIS
        raise