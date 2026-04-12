from sqlalchemy import Column, Integer, String, Date
from src.core.database import Base
import datetime

class User(Base):
    __tablename__ = "User"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(100), nullable=False)
    user_email = Column(String(100), nullable=False, unique=True)
    user_birth_date = Column(Date, nullable=False)
    user_registration_date = Column(Date, nullable=False, default=datetime.date.today)