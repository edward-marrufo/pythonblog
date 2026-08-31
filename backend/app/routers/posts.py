# app/routers/posts.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from backend.app.db import get_db
from backend.app.models.post import Post, PostCreate, Author
from backend.app.models.user import CurrentUser
from backend.app.core.security import get_current_user
from backend.app.core.permissions import require_post_owner
from backend.app.core.security import CurrentUser
import uuid

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("", response_model=Post)
def create_post(
    post: PostCreate,
    user: CurrentUser = Depends(get_current_user),  # Pydantic model
    db = Depends(get_db)
):
    try:
        with db.cursor() as cursor:
            # Convert user id to UUID for Postgres using dot notation
            user_id = uuid.UUID(user.id)
            
            cursor.execute(
                "INSERT INTO posts (title, text, user_id) VALUES (?,?,?) RETURNING id, title, text, created_at;",
                (post.title, post.text, user_id)
            )

            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=400, detail="Failed to insert post")
            
            db.commit()

        return Post(
            id=row[0],       # id from RETURNING
            title=row[1],
            text=row[2],
            created_at=row[3],
            author=Author(username=user.username),  # author object
            can_delete=True  # creator can always delete
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[Post])
def list_posts(
    limit: int = 10,
    user: CurrentUser = Depends(get_current_user),
    db = Depends(get_db)
):
    """Return a list of posts, up to `limit` rows, with author info and delete permissions."""
    posts = []

    with db.cursor() as cursor:
        # Fetch posts with author info
        cursor.execute(f"""
            SELECT posts.id, posts.title, posts.text, posts.created_at, users.username, posts.user_id
            FROM posts
            JOIN users ON posts.user_id = users.user_id
            ORDER BY posts.created_at DESC
            LIMIT {limit}
        """)
        rows = cursor.fetchall()

        for row in rows:
            post_id, title, text, created_at, username, post_user_id = row

            # Compute delete permission for current user
            can_delete = user.id == str(post_user_id) or user.role == "admin"

            posts.append(Post(
                id=post_id,
                title=title,
                text=text,
                created_at=created_at,
                author=Author(username=username),
                can_delete=can_delete
            ))

    return posts

@router.delete("/{post_id}")
def delete_post(
    post_id: str,
    user: dict = Depends(require_post_owner("post_id")),
    db = Depends(get_db)
):
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        db.commit()

    return {"message": "Post deleted"}