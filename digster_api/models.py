from email.policy import default
from sqlalchemy import Column, Float, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Date, DateTime
from pydantic import BaseModel, HttpUrl


Base = declarative_base()


class StreamingServiceMapping(Base):
    """Maps internal entities to external streaming service IDs."""
    __tablename__ = "streaming_service_mappings"
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True)  # 'album', 'track', 'artist'
    entity_id = Column(Integer, index=True)   # Internal ID (album.id, track.id, artist.id)
    service_name = Column(String, index=True) # 'spotify', 'deezer', etc.
    external_id = Column(String, index=True)  # External service ID
    created_at = Column(DateTime)


class AlbumRecRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    user_id: str
    album_image_url: HttpUrl
    album_name: str
    artist_name: str
    album_url: HttpUrl


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    display_name = Column(
        String,
    )
    email = Column(String)
    country = Column(String)
    description = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime)
    has_allowed_fetching = Column(Boolean, default=False)
    # Keep for backward compatibility during migration
    spotify_access_token = Column(String)
    spotify_refresh_token = Column(String)


class UserStreamingService(Base):
    """Links users to their streaming service accounts and tokens."""
    __tablename__ = "user_streaming_services"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    service_name = Column(String, index=True)  # 'spotify', 'deezer', etc.
    access_token = Column(String)
    refresh_token = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Listen(Base):
    __tablename__ = "listens"
    id = Column(Integer, primary_key=True, index=True)
    listened_at = Column(
        DateTime,
    )
    track_id = Column(String)
    user_id = Column(String)


class Track(Base):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True, index=True)
    # Keep for backward compatibility during migration
    spotify_id = Column(String, index=True)
    external_id = Column(String, index=True)  # Generic external ID for the primary service
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
    # Keep for backward compatibility during migration
    spotify_id = Column(String, index=True)
    external_id = Column(String, index=True)  # Generic external ID for the primary service
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
    created_at = Column(DateTime)
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


class Artist(Base):
    __tablename__ = "artists"
    id = Column(Integer, primary_key=True, index=True)
    # Keep for backward compatibility during migration
    spotify_id = Column(String, index=True)
    external_id = Column(String, index=True)  # Generic external ID for the primary service
    created_at = Column(DateTime)
    name = Column(String, index=True)
    genres = Column(String)
    followers = Column(Integer)
    popularity = Column(Integer)
    image_url = Column(String)


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


class Follow(Base):
    __tablename__ = "follows"
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(String, index=True)
    following_id = Column(String, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_following = Column(Boolean)
