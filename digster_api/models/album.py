"""Album-related models."""

from sqlalchemy import Column, Integer, String, DateTime, Date

from .base import Base


class Album(Base):
    __tablename__ = "albums"
    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String, index=True)
    artist_id = Column(Integer, index=True)
    created_at = Column(DateTime)
    type = Column(String)
    name = Column(String)
    upc_id = Column(String)
    genres = Column(String)
    image_url = Column(String)
    label = Column(String)
    popularity = Column(Integer)
    release_date = Column(String)
    total_tracks = Column(Integer)
    primary_color = Column(String)
    secondary_color = Column(String)
    tertiary_color = Column(String)
    fourth_color = Column(String)
    fifth_color = Column(String)
    fetched_genres_date = Column(DateTime)
    fetched_colors_date = Column(DateTime)


class UserAlbum(Base):
    __tablename__ = "user_albums"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    album_id = Column(Integer, index=True)
    added_at = Column(Date)
    created_at = Column(DateTime)


class AlbumGenre(Base):
    __tablename__ = "album_genres"
    id = Column(Integer, primary_key=True, index=True)
    album_id = Column(Integer, index=True)
    genre_id = Column(Integer, index=True)
    created_at = Column(DateTime)


class AlbumStyle(Base):
    __tablename__ = "album_styles"
    id = Column(Integer, primary_key=True, index=True)
    album_id = Column(Integer, index=True)
    style_id = Column(Integer, index=True)
    created_at = Column(DateTime)