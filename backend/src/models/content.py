from sqlalchemy import Column, Integer, String, Time, Date, ForeignKey, Table
from sqlalchemy.orm import relationship
from src.core.database import Base

content_genre_association = Table(
    "Is",
    Base.metadata,
    Column("content_id", Integer, ForeignKey("content.content_id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genre.genre_id", ondelete="CASCADE"), primary_key=True)
)

content_copyright_association = Table(
    "own",
    Base.metadata,
    Column("content_id", Integer, ForeignKey("content.content_id", ondelete="CASCADE"), primary_key=True),
    Column("copyright_holder_id", Integer, ForeignKey("copyright_holder.copyright_holder_id", ondelete="CASCADE"), primary_key=True)
)

content_tag_association = Table(
    "associate",
    Base.metadata,
    Column("content_id", Integer, ForeignKey("content.content_id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.tag_id", ondelete="CASCADE"), primary_key=True)
)

class Genre(Base):
    __tablename__ = "genre"
    genre_id = Column(Integer, primary_key=True, index=True)
    genre_name = Column(String(50), nullable=False)

class CopyrightHolder(Base):
    __tablename__ = "copyright_holder"
    copyright_holder_id = Column(Integer, primary_key=True, index=True)
    copyright_holder_name = Column(String(100), nullable=False)
    copyright_holder_phone = Column(String(15), nullable=False)
    copyright_holder_email = Column(String(100), nullable=False)

class Tag(Base):
    __tablename__ = "tag"
    tag_id = Column(Integer, primary_key=True, index=True)
    tag_name = Column(String(50), nullable=False)

class Content(Base):
    __tablename__ = "content"
    content_id = Column(Integer, primary_key=True, index=True)
    content_name = Column(String(100), nullable=False)
    content_duration = Column(Time, nullable=False)
    content_publish_date = Column(Date, nullable=False)
    content_description = Column("content_discription", String(500))
    content_type = Column(String(50))

    genres = relationship("Genre", secondary=content_genre_association, lazy="selectin")
    copyright_holders = relationship("CopyrightHolder", secondary=content_copyright_association, lazy="selectin")
    tags = relationship("Tag", secondary=content_tag_association, lazy="selectin")