# app/main.py
from fastapi import FastAPI
from backend.app.db_init import init_db
from backend.app.db import init_pool
#from backend.app.routers.authentication import auth_router
from backend.app.routers.api import api_router
from fastapi.middleware.cors import CORSMiddleware
import datetime

app = FastAPI(title="Posts API")

# Allow requests from your frontend
origins = [
    "http://localhost:5173",  # your dev React frontend
    # "http://127.0.0.1:5173", # optional
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # can also use ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],        # Content-Type, Authorization, etc.
)
print("Starting main")
#app.include_router(posts.router)
#app.include_router(users.router)
#app.include_router(authentication.auth_router, prefix="/auth")
app.include_router(api_router)

for route in app.routes:
    print(route.path)

@app.on_event("startup")
def startup():
    init_pool() # initialize our pool before we try to make any calls
    init_db()  # ensure posts table exists before any requests, safe retry builtin

@app.get("/")
def root():
    #getting the timestamp in ISO8601 UTC format
    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"Hello": "World", "Timestamp:": timestamp}