from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, Float, SmallInteger
from src.core.database import Base
from sqlalchemy.orm import relationship

class SubscribeType(Base):
    __tablename__ = "subscribe_type"

    subscribe_type_id = Column(Integer, primary_key=True)
    subscribe_type_discription = Column(Text, nullable=True)
    subscribe_type_name = Column(String(50), nullable=False)
    subscribe_type_max_type_quality = Column(SmallInteger, nullable=False)
    subscribe_type_cost = Column(Float, nullable=False)
    subscribe_type_duration = Column(Integer, nullable=False)

    subscriptions = relationship("Subscribe", back_populates="subscribe_type")

class Subscribe(Base):
    __tablename__ = "subscribe"

    subscribe_type_id = Column(Integer, ForeignKey("subscribe_type.subscribe_type_id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("User.user_id"), primary_key=True)
    subscribe_start = Column(Date, primary_key=True)
    subscribe_finish = Column(Date, nullable=False)

    user = relationship("User")
    subscribe_type = relationship("SubscribeType", back_populates="subscriptions")