# app/models/post.py
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

# class Post(BaseModel):
#     id: Optional[int] = None  # id is auto-incremented/assigned by our db
#     title: str                # required
#     text: Optional[str] = None  # optional text
#     created_at: Optional[datetime] = None #optional timestamp


# This is the model for Post model below

class Author(BaseModel):
    username: str

#This is the model for requests ie: client input
class PostCreate(BaseModel):
    title: str
    text: Optional[str] = None
    #Adding the below lines make it to where if you add anything extra
    #in the input, we returned a not allowed http response code
    class Config:
        extra = 'forbid'

#This is the model for responses ie: client output
class Post(BaseModel):
    id: int
    title: str
    author: Author
    text: Optional[str]
    created_at: datetime
    can_delete: bool