from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from src.core.database import Base
from sqlalchemy.orm import relationship

class Payment(Base):
    __tablename__ = "payment"

    user_id = Column(Integer, ForeignKey("User.user_id"), primary_key=True, nullable=False)
    payment_number = Column(Integer, primary_key=True, nullable=False)
    subscribe_type_id = Column(Integer, ForeignKey("subscribe_type.subscribe_type_id"), nullable=False)
    subscribe_start = Column(Date, nullable=True)
    payment_sum = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_method = Column(String(100), nullable=False)

    user = relationship("User", back_populates="payments")
    subscribe_type = relationship("SubscribeType")