# /app/routers/api.py

from fastapi import APIRouter

from backend.app.routers import posts, users, authentication


api_router = APIRouter(prefix="/api/v1")


api_router.include_router(posts.router)
api_router.include_router(users.router)
api_router.include_router(authentication.router)