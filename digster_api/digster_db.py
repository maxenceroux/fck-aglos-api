from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import create_engine, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

try:
    from models import (
        Album,
        AlbumGenre,
        AlbumStyle,
        Artist,
        Follow,
        Genre,
        Listen,
        StreamingServiceMapping,
        Style,
        Track,
        User,
        UserAlbum,
        UserStreamingService,
    )
except:
    from digster_api.models import (
        Album,
        AlbumGenre,
        AlbumStyle,
        Artist,
        Follow,
        Genre,
        Listen,
        StreamingServiceMapping,
        Style,
        Track,
        User,
        UserAlbum,
        UserStreamingService,
    )


class DigsterDB:
    def __init__(self, db_url: str) -> None:
        self.db = create_engine(db_url)
        self.session = sessionmaker(self.db)()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def get_user_spotify_tokens(self, user_id):
        token = (
            self.session.query(
                User.spotify_access_token, User.spotify_refresh_token
            )
            .filter(User.id == user_id)
            .first()
        )
        if token:
            return {"access_token": token[0], "refresh_token": token[1]}
        return None

    def get_user_info(self, user_id: str):
        return self.session.query(User).filter(User.id == user_id).first()

    def insert_user(self, user, access_token, refresh_token):
        db_user = (
            self.session.query(User).filter(User.id == user.get("id")).first()
        )

        if db_user:
            db_user.spotify_access_token = access_token
            db_user.spotify_refresh_token = refresh_token
        else:
            new_user = User(
                id=user.get("id"),
                created_at=datetime.now(),
                display_name=user.get("display_name"),
                email=user.get("email"),
                country=user.get("country"),
                description=user.get("description"),
                image_url=user.get("image_url"),
                spotify_access_token=access_token,
                spotify_refresh_token=refresh_token,
            )
            self.session.add(new_user)
        self.session.commit()

    def upsert_user(self, user: Dict[str, Any]) -> None:
        user["created_at"] = datetime.now()
        stmt = insert(User).values(user)
        stmt = stmt.on_conflict_do_update(
            constraint="users_pkey",
            set_={
                "display_name": stmt.excluded.display_name,
                "email": stmt.excluded.email,
                "country": stmt.excluded.country,
                "image_url": stmt.excluded.image_url,
            },
        )
        self.session.execute(stmt)
        self.session.commit()

    def insert_genre(self, genre: str) -> None:
        db_genre = (
            self.session.query(Genre).filter(Genre.genre == genre).first()
        )
        if not db_genre:
            new_genre = Genre(genre=genre, created_at=datetime.now())
            self.session.add(new_genre)
            self.session.commit()
            return new_genre.id
        else:
            return db_genre.id

    def insert_style(self, style: str) -> None:
        db_style = (
            self.session.query(Style).filter(Style.style == style).first()
        )
        if not db_style:
            new_style = Style(style=style, created_at=datetime.now())
            self.session.add(new_style)
            self.session.commit()
            return new_style.id
        else:
            return db_style.id

    def insert_artist(self, spotify_id: str, name: str) -> None:
        artist = (
            self.session.query(Artist)
            .filter(Artist.spotify_id == spotify_id)
            .first()
        )
        db_artist = Artist(
            spotify_id=spotify_id,
            name=name,
            created_at=datetime.now(),
        )
        if not artist:
            self.session.add(db_artist)
            self.session.commit()
            return db_artist.id
        else:
            return artist.id

    def insert_album(
        self,
        spotify_id: str,
        artist_id: int,
        type: str,
        upc_id: str,
        label: str,
        name: str,
        release_date: str,
        image_url: str,
        genres: str,
        total_tracks: int,
        popularity: int,
    ):
        album = (
            self.session.query(Album)
            .filter(Album.spotify_id == spotify_id)
            .first()
        )
        db_album = Album(
            spotify_id=spotify_id,
            artist_id=artist_id,
            type=type,
            upc_id=upc_id,
            label=label,
            name=name,
            release_date=release_date,
            image_url=image_url,
            genres=genres,
            total_tracks=total_tracks,
            popularity=popularity,
            created_at=datetime.now(),
        )
        if not album:
            self.session.add(db_album)
            self.session.commit()
            return db_album.id
        else:
            return album.id

    def insert_user_album(
        self, user_id: int, album_id: int, added_at: datetime.date
    ):
        user_album = (
            self.session.query(UserAlbum)
            .filter(UserAlbum.user_id == user_id)
            .filter(UserAlbum.album_id == album_id)
            .first()
        )
        db_user_album = UserAlbum(
            user_id=user_id,
            album_id=album_id,
            added_at=added_at,
            created_at=datetime.now(),
        )
        if not user_album:
            self.session.add(db_user_album)
            self.session.commit()

    def insert_album_genre(self, album_genre: Dict[str, Any]) -> None:
        album_genre.update({"created_at": datetime.now()})
        stmt = insert(AlbumGenre).values(album_genre)
        self.session.execute(stmt)
        self.session.commit()

    def insert_album_style(self, album_style: Dict[str, Any]) -> None:
        album_style.update({"created_at": datetime.now()})
        stmt = insert(AlbumStyle).values(album_style)
        self.session.execute(stmt)
        self.session.commit()

    def update_fetched_genres_date(self, album_id: int):
        album = self.session.query(Album).filter(Album.id == album_id).first()
        album.fetched_genres_date = datetime.now()
        self.session.commit()

    def update_fetched_colors_date(self, album_id: int):
        album = self.session.query(Album).filter(Album.id == album_id).first()
        album.fetched_colors_date = datetime.now()
        self.session.commit()

    def insert_listens(self, listens: List[Listen]) -> None:
        self.session.bulk_save_objects(listens)
        self.session.commit()

    def insert_tracks(self, tracks: List[Track]) -> None:
        self.session.bulk_save_objects(tracks)
        self.session.commit()

    def insert_albums(self, albums: List[Album]) -> None:
        self.session.bulk_save_objects(albums)
        self.session.commit()

    def insert_artists(self, artists: List[Artist]) -> None:
        self.session.bulk_save_objects(artists)
        self.session.commit()

    def run_select_query(self, query: str):
        results_list = self.session.execute(query).fetchall()
        return results_list

    def update_fetching_allowance(self, user_id: int, value):

        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(has_allowed_fetching=value)
        )
        self.session.execute(stmt)
        self.session.commit()

    def update_color_album(self, album_id: int, colors):

        stmt = (
            update(Album)
            .where(Album.id == album_id)
            .values(primary_color=colors[0], secondary_color=colors[1])
        )
        self.session.execute(stmt)
        self.session.commit()

    def update_description(self, user_id: int, description: str):
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(description=description)
        )
        self.session.execute(stmt)
        self.session.commit()

    def insert_follow(self, follow: Dict[str, Any]) -> None:
        follow.update(
            {"created_at": datetime.now(), "updated_at": datetime.now()}
        )
        stmt = insert(Follow).values(follow)
        self.session.execute(stmt)
        self.session.commit()

    def follows(self, follower_id: str, following_id: str):
        follow = (
            self.session.query(Follow)
            .filter(Follow.follower_id == follower_id)
            .filter(Follow.following_id == following_id)
            .first()
        )
        if follow:
            return True
        return False

    def update_follow(self, follow: Dict[str, Any]):
        stmt = (
            update(Follow)
            .where(Follow.following_id == follow["following_id"])
            .where(Follow.follower_id == follow["follower_id"])
            .values(
                updated_at=datetime.now(), is_following=follow["is_following"]
            )
        )
        self.session.execute(stmt)
        self.session.commit()

    def close_conn(self):
        self.db.dispose()

    # Platform-agnostic streaming service methods
    def get_user_streaming_tokens(self, user_id: str, service_name: str):
        """Get user tokens for a specific streaming service."""
        user_service = (
            self.session.query(UserStreamingService)
            .filter(UserStreamingService.user_id == user_id)
            .filter(UserStreamingService.service_name == service_name)
            .first()
        )
        if user_service:
            return {
                "access_token": user_service.access_token,
                "refresh_token": user_service.refresh_token
            }
        # Fallback to legacy Spotify tokens for backward compatibility
        if service_name == "spotify":
            return self.get_user_spotify_tokens(user_id)
        return None

    def upsert_user_streaming_service(self, user_id: str, service_name: str, access_token: str, refresh_token: str):
        """Insert or update user streaming service tokens."""
        user_service = (
            self.session.query(UserStreamingService)
            .filter(UserStreamingService.user_id == user_id)
            .filter(UserStreamingService.service_name == service_name)
            .first()
        )
        
        if user_service:
            user_service.access_token = access_token
            user_service.refresh_token = refresh_token
            user_service.updated_at = datetime.now()
        else:
            new_user_service = UserStreamingService(
                user_id=user_id,
                service_name=service_name,
                access_token=access_token,
                refresh_token=refresh_token,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.session.add(new_user_service)
        
        self.session.commit()

    def add_streaming_service_mapping(self, entity_type: str, entity_id: int, service_name: str, external_id: str):
        """Add a mapping between internal entity and external service ID."""
        existing = (
            self.session.query(StreamingServiceMapping)
            .filter(StreamingServiceMapping.entity_type == entity_type)
            .filter(StreamingServiceMapping.entity_id == entity_id)
            .filter(StreamingServiceMapping.service_name == service_name)
            .first()
        )
        
        if not existing:
            mapping = StreamingServiceMapping(
                entity_type=entity_type,
                entity_id=entity_id,
                service_name=service_name,
                external_id=external_id,
                created_at=datetime.now()
            )
            self.session.add(mapping)
            self.session.commit()

    def get_external_id(self, entity_type: str, entity_id: int, service_name: str) -> str:
        """Get external service ID for an internal entity."""
        mapping = (
            self.session.query(StreamingServiceMapping)
            .filter(StreamingServiceMapping.entity_type == entity_type)
            .filter(StreamingServiceMapping.entity_id == entity_id)
            .filter(StreamingServiceMapping.service_name == service_name)
            .first()
        )
        return mapping.external_id if mapping else None

    def get_entity_by_external_id(self, entity_type: str, service_name: str, external_id: str) -> int:
        """Get internal entity ID by external service ID."""
        mapping = (
            self.session.query(StreamingServiceMapping)
            .filter(StreamingServiceMapping.entity_type == entity_type)
            .filter(StreamingServiceMapping.service_name == service_name)
            .filter(StreamingServiceMapping.external_id == external_id)
            .first()
        )
        return mapping.entity_id if mapping else None

    def insert_artist_platform_agnostic(self, external_id: str, name: str, service_name: str = 'spotify') -> int:
        """Insert artist with platform-agnostic approach."""
        # Check if artist already exists by external service mapping
        existing_id = self.get_entity_by_external_id('artist', service_name, external_id)
        if existing_id:
            return existing_id
        
        # Check legacy spotify_id for backward compatibility
        if service_name == 'spotify':
            artist = (
                self.session.query(Artist)
                .filter(Artist.spotify_id == external_id)
                .first()
            )
            if artist:
                # Create mapping for existing artist
                self.add_streaming_service_mapping('artist', artist.id, service_name, external_id)
                return artist.id
        
        # Create new artist
        db_artist = Artist(
            external_id=external_id,
            name=name,
            created_at=datetime.now(),
        )
        # Keep spotify_id for backward compatibility
        if service_name == 'spotify':
            db_artist.spotify_id = external_id
            
        self.session.add(db_artist)
        self.session.commit()
        
        # Add mapping
        self.add_streaming_service_mapping('artist', db_artist.id, service_name, external_id)
        
        return db_artist.id

    def insert_album_platform_agnostic(
        self,
        external_id: str,
        artist_id: int,
        type: str,
        upc_id: str,
        label: str,
        name: str,
        genres: str,
        image_url: str,
        popularity: int,
        release_date: str,
        total_tracks: int,
        service_name: str = 'spotify'
    ) -> int:
        """Insert album with platform-agnostic approach."""
        # Check if album already exists by external service mapping
        existing_id = self.get_entity_by_external_id('album', service_name, external_id)
        if existing_id:
            return existing_id
        
        # Check legacy spotify_id for backward compatibility
        if service_name == 'spotify':
            album = (
                self.session.query(Album)
                .filter(Album.spotify_id == external_id)
                .first()
            )
            if album:
                # Create mapping for existing album
                self.add_streaming_service_mapping('album', album.id, service_name, external_id)
                return album.id
        
        # Create new album
        db_album = Album(
            external_id=external_id,
            artist_id=artist_id,
            created_at=datetime.now(),
            type=type,
            name=name,
            upc_id=upc_id,
            genres=genres,
            image_url=image_url,
            label=label,
            popularity=popularity,
            release_date=release_date,
            total_tracks=total_tracks,
        )
        # Keep spotify_id for backward compatibility
        if service_name == 'spotify':
            db_album.spotify_id = external_id
            
        self.session.add(db_album)
        self.session.commit()
        
        # Add mapping
        self.add_streaming_service_mapping('album', db_album.id, service_name, external_id)
        
        return db_album.id
