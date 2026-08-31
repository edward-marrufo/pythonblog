# app/models/user.py
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

# class Post(BaseModel):
#     id: Optional[int] = None  # id is auto-incremented/assigned by our db
#     title: str                # required
#     text: Optional[str] = None  # optional text
#     created_at: Optional[datetime] = None #optional timestamp

#This is the model for requests ie: client input / request DTO
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

#This is the model for responses ie: client output / response DTO
class User(BaseModel):
    username: str
    created_at: datetime

# This is the model for responses ie: client output / auth context model
class CurrentUser(BaseModel):
    id: str
    username: str
    role: str