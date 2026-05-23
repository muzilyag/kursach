from pydantic import BaseModel, ConfigDict
from datetime import time, date
from typing import Optional, List


class AdvertisingBase(BaseModel):
    advertising_name: Optional[str] = None
    advertising_duration: time
    advertising_owner: str
    advertising_start_date: date
    advertising_finish_date: date


class AdvertisingCreate(AdvertisingBase):
    tag_ids: List[int] = []


class AdvertisingUpdate(BaseModel):
    advertising_name: Optional[str] = None
    advertising_duration: Optional[time] = None
    advertising_owner: Optional[str] = None
    advertising_start_date: Optional[date] = None
    advertising_finish_date: Optional[date] = None
    tag_ids: Optional[List[int]] = None


class AdvertisingResponse(AdvertisingBase):
    advertising_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class AdvertisingListResponse(BaseModel):
    items: list[AdvertisingResponse]
    total: int
