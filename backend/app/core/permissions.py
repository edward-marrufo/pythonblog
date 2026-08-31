#/backend/app/core/permissions.py
from fastapi import Request, HTTPException, Depends
from backend.app.core.security import get_current_user
from backend.app.db import get_db

def require_post_owner(post_id_param: str = "post_id"):
    def dependency(
        request: Request,
        user: dict = Depends(get_current_user),
        db = Depends(get_db)
    ):
        post_id = request.path_params[post_id_param]
        cursor = db.cursor()
        cursor.execute("SELECT user_id FROM posts WHERE id = ?", (post_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Post not found")
        if user.id != str(row[0]) and user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        return user
    return dependency