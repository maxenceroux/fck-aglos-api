from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Date, DateTime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    display_name = Column(
        String,
    )
    email = Column(String)
    country = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime)


class Listen(Base):
    __tablename__ = "listens"
    id = Column(Integer, primary_key=True, index=True)
    listened_at = Column(
        DateTime,
    )
    track_id = Column(String)
    user_id = Column(Integer)


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


class Album(Base):
    __tablename__ = "albums"
    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String, index=True)
    artist_id = Column(String, index=True)
    created_at = Column(DateTime)
    name = Column(String)
    genres = Column(String)
    image_url = Column(String)
    label = Column(String)
    popularity = Column(Integer)
    release_date = Column(Date)
    total_tracks = Column(Integer)


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
