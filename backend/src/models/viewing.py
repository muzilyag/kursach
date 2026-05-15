from sqlalchemy import Column, Integer, ForeignKey, DateTime, CheckConstraint
from src.core.database import Base
import datetime

class Viewing(Base):
    __tablename__ = "viewing"

    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"), primary_key=True)
    content_id = Column(Integer, ForeignKey("content.content_id", ondelete="RESTRICT"), primary_key=True)
    viewing_progress = Column(Integer, nullable=False)
    viewing_start = Column(DateTime, nullable=False, default=datetime.datetime.now)
    viewing_finish = Column(DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    __table_args__ = (
        CheckConstraint('viewing_progress >= 0 AND viewing_progress <= 100', name='viewing_percent_check'),
    )