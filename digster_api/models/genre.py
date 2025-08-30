"""Genre and style-related models."""

from sqlalchemy import Column, Integer, String, DateTime

from .base import Base


class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True, index=True)
    genre = Column(String, index=True)
    created_at = Column(DateTime)


class Style(Base):
    __tablename__ = "styles"
    id = Column(Integer, primary_key=True, index=True)
    style = Column(String, index=True)
    created_at = Column(DateTime)