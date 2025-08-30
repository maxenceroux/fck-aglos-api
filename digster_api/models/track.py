"""Track and listening-related models."""

from sqlalchemy import Column, Integer, String, Float, DateTime

from .base import Base


class Track(Base):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String, index=True)
    created_at = Column(DateTime)
    name = Column(String)
    duration_ms = Column(Integer)
    popularity = Column(Integer)
    album_id = Column(String)
    danceability = Column(Float)
    energy = Column(Float)
    key = Column(Float)
    loudness = Column(Float)
    mode = Column(Float)
    speechiness = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    liveness = Column(Float)
    valence = Column(Float)
    tempo = Column(Float)


class Listen(Base):
    __tablename__ = "listens"
    id = Column(Integer, primary_key=True, index=True)
    listened_at = Column(DateTime)
    track_id = Column(String)
    user_id = Column(String)