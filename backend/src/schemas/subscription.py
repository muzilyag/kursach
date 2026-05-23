from pydantic import BaseModel
from datetime import date


class SubscriptionChange(BaseModel):
    user_id: int
    subscribe_type_id: int
    payment_method: str


class SubscriptionUpdate(BaseModel):
    subscribe_finish: date


class SubscriptionCreate(BaseModel):
    user_id: int
    subscribe_type_id: int
    subscribe_start: date
    subscribe_finish: date


class UserSubscriptionBuy(BaseModel):
    subscribe_type_id: int
    payment_method: str = "карта"
