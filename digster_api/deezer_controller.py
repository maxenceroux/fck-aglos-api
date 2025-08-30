import logging
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

from .streaming_service_interface import StreamingServiceInterface

load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)


class DeezerAPIError(Exception):
    """Custom exception for Deezer API errors."""

    pass


class DeezerAuthenticationError(DeezerAPIError):
    """Exception raised when authentication fails."""

    pass


class DeezerController(StreamingServiceInterface):
    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self._base_url = "https://api.deezer.com"

    def get_unauth_token(self) -> str:
        """Get an unauthenticated token for API access.

        Note: Deezer API doesn't require authentication for most read
        operations. This method returns a placeholder token to maintain
        interface compatibility.
        """
        # Deezer API allows many operations without authentication
        # Return a placeholder to maintain interface compatibility
        return "deezer_public_access"

    def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh the access token using a refresh token."""
        # Deezer uses OAuth 2.0 flow
        url = "https://connect.deezer.com/oauth/access_token.php"
        params = {
            "app_id": self.client_id,
            "secret": self.client_secret,
            "refresh_token": refresh_token,
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to refresh access token: {err}")
            raise DeezerAuthenticationError(
                f"Failed to refresh access token: {err}"
            ) from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while refreshing access token: {err}")
            raise DeezerAPIError(
                f"Network error while refreshing access token: {err}"
            ) from err

        # Deezer returns URL-encoded response
        response_text = response.text
        if "access_token=" in response_text:
            # Parse the access_token from the response
            token = response_text.split("access_token=")[1].split("&")[0]
            return token
        else:
            logger.error("No access token received in refresh response")
            raise DeezerAuthenticationError(
                "No access token received in refresh response"
            )

    def get_current_play(self, token: str) -> Dict[str, Any]:
        """Get the currently playing track for the user.

        Note: Deezer API doesn't provide a direct endpoint for current
        playback. This is a limitation compared to Spotify.
        """
        # Deezer doesn't have a current playback endpoint like Spotify
        # Return empty dict to indicate no current track available
        logger.warning("Deezer API doesn't support getting current playback")
        return {}

    def save_album(
        self, tokens: Dict[str, Any], album_id: str
    ) -> Dict[str, Any]:
        """Save an album to the user's library."""
        url = f"{self._base_url}/user/me/albums"
        params = {
            "access_token": tokens.get("access_token"),
            "album_id": album_id,
        }

        try:
            response = requests.post(url, params=params)
            if response.status_code == 401:
                logger.info("Access token expired, refreshing tokens...")
                tokens["access_token"] = self.refresh_access_token(
                    tokens["refresh_token"]
                )
                return self.save_album(tokens, album_id)
            response.raise_for_status()

            # Deezer returns boolean true on success
            response_data = response.json()
            if response_data is True:
                return {
                    "status": "success",
                    "message": "Album saved successfully",
                }
            else:
                return {"status": "error", "message": "Failed to save album"}

        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to save album {album_id}: {err}")
            raise DeezerAPIError(
                f"Failed to save album {album_id}: {err}"
            ) from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while saving album {album_id}: {err}")
            raise DeezerAPIError(
                f"Network error while saving album {album_id}: {err}"
            ) from err

    def get_user_info(self, token: str) -> Dict[str, Any]:
        """Get user information."""
        url = f"{self._base_url}/user/me"
        params = {"access_token": token}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to get user info: {err}")
            raise DeezerAPIError(f"Failed to get user info: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting user info: {err}")
            raise DeezerAPIError(
                f"Network error while getting user info: {err}"
            ) from err

        response_data = response.json()
        current_user = {
            "id": str(response_data.get("id")),
            "display_name": response_data.get("name"),
            "email": response_data.get("email"),
            "country": response_data.get("country"),
            "image_url": response_data.get("picture_medium"),
        }
        return current_user

    def get_recently_played(
        self,
        token: str,
        url: Optional[str] = None,
        after: Optional[int] = None,
        limit: Optional[int] = 50,
    ) -> Dict[str, Any]:
        """Get recently played tracks.

        Note: Deezer API doesn't provide recently played tracks.
        This is a limitation compared to Spotify.
        """
        # Deezer doesn't have a recently played endpoint
        logger.warning("Deezer API doesn't support recently played tracks")
        return {"next_url": None, "recently_played": []}

    def get_tracks_info(
        self, token: str, track_ids: List[str]
    ) -> Dict[str, Any]:
        """Get information about specific tracks."""
        if not track_ids:
            return {"message": "No track IDs provided"}

        # Deezer allows multiple track requests via comma-separated IDs
        track_ids_str = ",".join(track_ids)
        url = f"{self._base_url}/track/{track_ids_str}"

        # Add access token if provided (not required for track info)
        params = {}
        if token != "deezer_public_access":
            params["access_token"] = token

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to get tracks info: {err}")
            raise DeezerAPIError(f"Failed to get tracks info: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting tracks info: {err}")
            raise DeezerAPIError(
                f"Network error while getting tracks info: {err}"
            ) from err

        response_data = response.json()

        # Handle single track vs multiple tracks response
        if isinstance(response_data, dict) and "data" not in response_data:
            # Single track response
            tracks_data = [response_data]
        elif isinstance(response_data, dict) and "data" in response_data:
            # Multiple tracks response
            tracks_data = response_data["data"]
        else:
            tracks_data = []

        if not tracks_data:
            return {"message": "IDs corresponding to no tracks"}

        tracks_info = []
        for track in tracks_data:
            if track and track.get("id"):  # track can be None for invalid IDs
                tracks_info.append(
                    {
                        "deezer_id": str(track.get("id")),
                        "name": track.get("title"),
                        "duration_ms": track.get("duration", 0)
                        * 1000,  # Deezer returns seconds
                        "popularity": track.get(
                            "rank", 0
                        ),  # Deezer uses rank instead of popularity
                        "album_id": (
                            str(track.get("album", {}).get("id"))
                            if track.get("album")
                            else None
                        ),
                    }
                )

        return {"tracks_info": tracks_info}

    def get_tracks_attributes(
        self, token: str, track_ids: List[str]
    ) -> Dict[str, Any]:
        """Get audio features/attributes for specific tracks.

        Note: Deezer API doesn't provide audio features like Spotify.
        This returns empty results to maintain interface compatibility.
        """
        # Deezer doesn't have audio features like Spotify
        logger.warning("Deezer API doesn't support audio features/attributes")
        return {"message": "Deezer API doesn't support audio features"}

    def get_albums_info(
        self, token: str, album_ids: List[str]
    ) -> Dict[str, Any]:
        """Get information about specific albums."""
        if not album_ids:
            return {"message": "No album IDs provided"}

        albums = []

        # Deezer requires individual requests for each album
        for album_id in album_ids:
            url = f"{self._base_url}/album/{album_id}"

            # Add access token if provided (not required for album info)
            params = {}
            if token != "deezer_public_access":
                params["access_token"] = token

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                album_data = response.json()

                if album_data and album_data.get("id"):
                    albums.append(
                        {
                            "deezer_id": str(album_data.get("id")),
                            "artist_id": (
                                str(album_data.get("artist", {}).get("id"))
                                if album_data.get("artist")
                                else None
                            ),
                            "genres": " - ".join(
                                [
                                    genre.get("name", "")
                                    for genre in album_data.get(
                                        "genres", {}
                                    ).get("data", [])
                                ]
                            ),
                            "image_url": album_data.get("cover_medium"),
                            "label": album_data.get("label"),
                            "name": album_data.get("title"),
                            "popularity": album_data.get(
                                "fans", 0
                            ),  # Deezer uses fans count
                            "release_date": album_data.get("release_date"),
                            "total_tracks": album_data.get("nb_tracks", 0),
                        }
                    )

            except requests.exceptions.HTTPError as err:
                logger.warning(f"Failed to get album {album_id}: {err}")
                continue
            except requests.exceptions.RequestException as err:
                logger.warning(
                    f"Network error while getting album {album_id}: {err}"
                )
                continue

        if not albums:
            return {"message": "IDs corresponding to no albums"}

        return {"albums": albums}

    def get_artists_info(
        self, token: str, artist_ids: List[str]
    ) -> Dict[str, Any]:
        """Get information about specific artists."""
        if not artist_ids:
            return {"message": "No artist IDs provided"}

        artists = []

        # Deezer requires individual requests for each artist
        for artist_id in artist_ids:
            url = f"{self._base_url}/artist/{artist_id}"

            # Add access token if provided (not required for artist info)
            params = {}
            if token != "deezer_public_access":
                params["access_token"] = token

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                artist_data = response.json()

                if artist_data and artist_data.get("id"):
                    artists.append(
                        {
                            "deezer_id": str(artist_data.get("id")),
                            "name": artist_data.get("name"),
                            "popularity": artist_data.get(
                                "nb_fan", 0
                            ),  # Deezer uses fan count
                            "image_url": artist_data.get("picture_medium"),
                            "genres": "",  # Deezer doesn't provide artist
                            # genres directly
                        }
                    )

            except requests.exceptions.HTTPError as err:
                logger.warning(f"Failed to get artist {artist_id}: {err}")
                continue
            except requests.exceptions.RequestException as err:
                logger.warning(
                    f"Network error while getting artist {artist_id}: {err}"
                )
                continue

        if not artists:
            return {"message": "IDs corresponding to no artists"}

        return {"artists": artists}

    def get_user_saved_albums_limit(
        self,
        tokens: Dict[str, Any],
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get user's saved albums with pagination."""
        url = f"{self._base_url}/user/me/albums"
        params = {
            "access_token": tokens.get("access_token"),
            "limit": limit,
            "index": offset,  # Deezer uses 'index' instead of 'offset'
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 401:
                logger.info("Access token expired, refreshing tokens...")
                tokens["access_token"] = self.refresh_access_token(
                    tokens["refresh_token"]
                )
                params["access_token"] = tokens["access_token"]
                response = requests.get(url, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to get user saved albums: {err}")
            raise DeezerAPIError(
                f"Failed to get user saved albums: {err}"
            ) from err
        except requests.exceptions.RequestException as err:
            logger.error(
                f"Network error while getting user saved albums: {err}"
            )
            raise DeezerAPIError(
                f"Network error while getting user saved albums: {err}"
            ) from err

        response_data = response.json()
        albums_data = response_data.get("data", [])

        albums = []
        user_albums = []

        for album in albums_data:
            if album:
                album_info = {
                    "deezer_id": str(album.get("id")),
                    "name": album.get("title"),
                    "artist_id": (
                        str(album.get("artist", {}).get("id"))
                        if album.get("artist")
                        else None
                    ),
                    "image_url": album.get("cover_medium"),
                    "release_date": album.get("release_date"),
                    "total_tracks": album.get("nb_tracks", 0),
                }
                albums.append(album_info)

                user_album = {
                    "album_id": str(album.get("id")),
                    "time_added": album.get(
                        "time_add"
                    ),  # Deezer provides time_add
                }
                user_albums.append(user_album)

        return {
            "albums": albums,
            "user_albums": user_albums,
            "next": response_data.get("next"),
            "total": response_data.get("total", len(albums)),
        }

    def get_user_saved_albums(
        self, token: str, user_id: str
    ) -> Dict[str, Any]:
        """Get all user's saved albums."""
        albums = []
        user_albums = []
        offset = 0
        limit = 50

        # Create tokens dict for compatibility with get_user_saved_albums_limit
        tokens = {"access_token": token}

        while True:
            try:
                result = self.get_user_saved_albums_limit(
                    tokens, limit=limit, offset=offset
                )

                page_albums = result.get("albums", [])
                page_user_albums = result.get("user_albums", [])

                albums.extend(page_albums)
                user_albums.extend(page_user_albums)

                # Check if there are more pages
                if not result.get("next") or len(page_albums) < limit:
                    break

                offset += limit

            except DeezerAPIError:
                logger.warning(f"Failed to get albums page at offset {offset}")
                break  # Don't fail completely, just stop pagination

        return {"albums": albums, "user_albums": user_albums}
