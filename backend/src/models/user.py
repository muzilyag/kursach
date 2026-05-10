from sqlalchemy import Column, Integer, String, Date
from src.core.database import Base
from sqlalchemy.orm import relationship
import datetime

class User(Base):
    __tablename__ = "User"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(100), nullable=False)
    user_email = Column(String(100), nullable=False, unique=True)
    user_birth_date = Column(Date, nullable=False)
    user_registration_date = Column(Date, nullable=False, default=datetime.date.today)
    user_password = Column(String(255), nullable=False)
    user_role = Column(String(20), nullable=False, default='user')

    subscriptions = relationship("Subscribe", back_populates="user")
    payments = relationship("Payment", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.user_id}, name='{self.user_name}', role='{self.user_role}')>"