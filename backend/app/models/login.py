# app/models/login.py
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

#This is the model for requests ie: client input
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    username: str