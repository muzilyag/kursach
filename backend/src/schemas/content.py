from pydantic import BaseModel
from datetime import date, time
from typing import Optional

class ContentCreate(BaseModel):
    content_name: str
    content_type: str
    content_duration: time
    content_publish_date: date
    content_discription: Optional[str] = None
    genre_id: Optional[int] = None
    copyright_holder_id: Optional[int] = None
    tag_id: Optional[int] = None