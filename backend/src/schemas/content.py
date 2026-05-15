from pydantic import BaseModel, EmailStr, Field
from datetime import date, time
from typing import Optional, List

class TagBase(BaseModel):
    tag_name: str

class TagCreate(TagBase):
    content_ids: List[int] = []

class TagRead(TagBase):
    tag_id: int
    class Config:
        from_attributes = True

class CopyrightHolderBase(BaseModel):
    copyright_holder_name: str
    copyright_holder_phone: str
    copyright_holder_email: EmailStr

class CopyrightHolderCreate(CopyrightHolderBase):
    content_ids: List[int] = []

class CopyrightHolderRead(BaseModel):
    copyright_holder_id: int
    copyright_holder_name: str
    copyright_holder_phone: str
    copyright_holder_email: str
    class Config:
        from_attributes = True

class GenreRead(BaseModel):
    genre_id: int
    genre_name: str
    class Config:
        from_attributes = True

class ContentRead(BaseModel):
    content_id: int
    content_name: str
    content_type: str
    content_duration: time
    content_publish_date: date
    content_discription: Optional[str] = None
    genres: List[GenreRead] = []
    copyright_holders: List[CopyrightHolderRead] = []
    tags: List[TagRead] = []
    class Config:
        from_attributes = True

class ContentCreate(BaseModel):
    content_name: str
    content_type: str
    content_duration: time
    content_publish_date: date
    content_discription: Optional[str] = None
    genre_ids: List[int] = []
    copyright_holder_ids: List[int] = []
    tag_ids: List[int] = []


class ViewingUpdate(BaseModel):
    progress: int