from sqlalchemy import Column, Integer, String, Time, Date
from src.core.database import Base


class Advertising(Base):
    __tablename__ = "advertising"

    advertising_id = Column(
        "advetising_id", Integer, primary_key=True, autoincrement=True
    )
    advertising_name = Column(String(100), nullable=True)
    advertising_duration = Column(Time, nullable=False)
    advertising_owner = Column(String(100), nullable=False)
    advertising_start_date = Column(Date, nullable=False)
    advertising_finish_date = Column(Date, nullable=False)
