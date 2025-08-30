"""User-related models."""

from sqlalchemy import Column, String, Boolean, DateTime, Integer

from .base import Base


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    display_name = Column(String)
    email = Column(String)
    country = Column(String)
    description = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime)
    has_allowed_fetching = Column(Boolean, default=False)
    spotify_access_token = Column(String)
    spotify_refresh_token = Column(String)


class Follow(Base):
    __tablename__ = "follows"
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(String, index=True)
    following_id = Column(String, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_following = Column(Boolean)