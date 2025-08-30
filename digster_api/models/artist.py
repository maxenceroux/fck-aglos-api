"""Artist-related models."""

from sqlalchemy import Column, Integer, String, DateTime

from .base import Base


class Artist(Base):
    __tablename__ = "artists"
    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String, index=True)
    created_at = Column(DateTime)
    name = Column(String, index=True)
    genres = Column(String)
    followers = Column(Integer)
    popularity = Column(Integer)
    image_url = Column(String)