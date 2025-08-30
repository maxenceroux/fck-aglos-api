import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import time
import hashlib
import hmac
import base64

import requests

from .streaming_service_interface import StreamingServiceInterface

# Configure logger
logger = logging.getLogger(__name__)


class AppleMusicAPIError(Exception):
    """Custom exception for Apple Music API errors."""
    pass


class AppleMusicAuthenticationError(AppleMusicAPIError):
    """Exception raised when authentication fails."""
    pass


class AppleMusicController(StreamingServiceInterface):
    def __init__(self, client_id: str, client_secret: str) -> None:
        """Initialize Apple Music client.
        
        Args:
            client_id: Team ID from Apple Developer account
            client_secret: Key ID (for simplicity, using this for key ID)
        """
        self.team_id = client_id
        self.key_id = client_secret
        self._base_url = "https://api.music.apple.com"
        # For demo purposes, using a placeholder private key
        # In production, this would be loaded from a secure location
        self._private_key = self._get_demo_private_key()

    def _get_demo_private_key(self) -> str:
        """Get a demo private key for testing purposes.
        
        In production, this would load the actual .p8 private key file.
        """
        return """-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg4f8lZLEWPpLcOcvs
a6Z3mOSQZ6BI0pEL6qHUW2YgJGahRANCAAQ0ZzMTIGq+eiTlQEiZ/mBhJM+nJK5M
E+mKNAHjFEbN4JAqRgxKX8BqAABODmJpjWDdmGhYY8Xo5SHxq2eLBH+v
-----END PRIVATE KEY-----"""

    def _generate_jwt_token(self) -> str:
        """Generate JWT token for Apple Music API authentication."""
        now = int(time.time())
        
        # JWT Header
        header = {
            "alg": "ES256",
            "kid": self.key_id
        }
        
        # JWT Payload
        payload = {
            "iss": self.team_id,
            "iat": now,
            "exp": now + 3600  # Token expires in 1 hour
        }
        
        # For demo purposes, return a mock JWT token
        # In production, this would use the actual private key to sign
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).decode().rstrip('=')
        
        # Mock signature for demo
        signature = base64.urlsafe_b64encode(
            f"mock_signature_{self.team_id}_{self.key_id}".encode()
        ).decode().rstrip('=')
        
        return f"{header_b64}.{payload_b64}.{signature}"

    def get_unauth_token(self) -> str:
        """Get an unauthenticated token for API access."""
        try:
            token = self._generate_jwt_token()
            logger.info("Successfully generated Apple Music developer token")
            return token
        except Exception as err:
            logger.error(f"Failed to generate Apple Music token: {err}")
            raise AppleMusicAuthenticationError(
                f"Failed to generate Apple Music token: {err}"
            ) from err

    def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh the access token using a refresh token.
        
        Note: Apple Music uses JWT tokens that are generated on-demand
        rather than OAuth2 refresh tokens.
        """
        try:
            # For Apple Music, we generate a new JWT token
            return self._generate_jwt_token()
        except Exception as err:
            logger.error(f"Failed to refresh Apple Music token: {err}")
            raise AppleMusicAuthenticationError(
                f"Failed to refresh Apple Music token: {err}"
            ) from err

    def get_current_play(self, token: str) -> Dict[str, Any]:
        """Get the currently playing track for the user.
        
        Note: Apple Music API requires user authorization for playback info.
        This is a limitation for public API access.
        """
        # Apple Music API doesn't provide current playback for public access
        # This would require user-specific authorization
        logger.warning("Apple Music API doesn't support getting current playback without user authorization")
        return {}

    def save_album(self, tokens: Dict[str, Any], album_id: str) -> Dict[str, Any]:
        """Save an album to the user's library.
        
        Note: This requires user authorization which is beyond the scope
        of the current implementation.
        """
        logger.warning("Apple Music library operations require user authorization")
        return {
            "status": "error",
            "message": "Apple Music library operations require user authorization"
        }

    def get_user_info(self, token: str) -> Dict[str, Any]:
        """Get user information.
        
        Note: Apple Music API requires user authorization for user info.
        """
        logger.warning("Apple Music user info requires user authorization")
        return {
            "id": "apple_music_user",
            "display_name": "Apple Music User",
            "email": None,
            "country": None,
            "image_url": None
        }

    def get_recently_played(
        self,
        token: str,
        url: Optional[str] = None,
        after: Optional[int] = None,
        limit: Optional[int] = 50,
    ) -> Dict[str, Any]:
        """Get recently played tracks.
        
        Note: Requires user authorization.
        """
        logger.warning("Apple Music recently played tracks require user authorization")
        return {"tracks": []}

    def get_tracks_info(
        self, token: str, track_ids: List[str]
    ) -> Dict[str, Any]:
        """Get information about specific tracks."""
        if not track_ids:
            return {"tracks": []}

        # Convert track_ids to Apple Music format if needed
        ids_param = ",".join(track_ids)
        url = f"{self._base_url}/v1/catalog/us/songs"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        params = {"ids": ids_param}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to get tracks info: {err}")
            raise AppleMusicAPIError(f"Failed to get tracks info: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting tracks info: {err}")
            raise AppleMusicAPIError(
                f"Network error while getting tracks info: {err}"
            ) from err

        response_data = response.json()
        tracks = []
        
        for track_data in response_data.get("data", []):
            attributes = track_data.get("attributes", {})
            tracks.append({
                "id": track_data.get("id"),
                "name": attributes.get("name"),
                "artist_name": attributes.get("artistName"),
                "album_name": attributes.get("albumName"),
                "duration_ms": attributes.get("durationInMillis"),
                "preview_url": attributes.get("previews", [{}])[0].get("url"),
                "external_urls": {
                    "apple_music": attributes.get("url")
                }
            })

        return {"tracks": tracks}

    def get_tracks_attributes(
        self, token: str, track_ids: List[str]
    ) -> Dict[str, Any]:
        """Get audio features/attributes for specific tracks.
        
        Note: Apple Music API doesn't provide detailed audio features
        like Spotify does.
        """
        logger.warning("Apple Music API doesn't provide detailed audio features")
        return {
            "audio_features": [
                {
                    "id": track_id,
                    "danceability": None,
                    "energy": None,
                    "key": None,
                    "loudness": None,
                    "mode": None,
                    "speechiness": None,
                    "acousticness": None,
                    "instrumentalness": None,
                    "liveness": None,
                    "valence": None,
                    "tempo": None,
                    "duration_ms": None
                }
                for track_id in track_ids
            ]
        }

    def get_albums_info(
        self, token: str, album_ids: List[str]
    ) -> Dict[str, Any]:
        """Get information about specific albums."""
        if not album_ids:
            return {"albums": []}

        albums = []
        for album_id in album_ids:
            url = f"{self._base_url}/v1/catalog/us/albums/{album_id}"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                response_data = response.json()
                if "data" in response_data and response_data["data"]:
                    album_data = response_data["data"][0]
                    attributes = album_data.get("attributes", {})
                    
                    albums.append({
                        "id": album_data.get("id"),
                        "name": attributes.get("name"),
                        "artist_name": attributes.get("artistName"),
                        "release_date": attributes.get("releaseDate"),
                        "total_tracks": attributes.get("trackCount"),
                        "genres": attributes.get("genreNames", []),
                        "image_url": attributes.get("artwork", {}).get("url"),
                        "external_urls": {
                            "apple_music": attributes.get("url")
                        }
                    })
                    
            except requests.exceptions.HTTPError as err:
                logger.error(f"Failed to get album {album_id}: {err}")
                continue
            except requests.exceptions.RequestException as err:
                logger.error(f"Network error while getting album {album_id}: {err}")
                continue

        if not albums:
            return {"message": "IDs corresponding to no albums"}

        return {"albums": albums}

    def get_artists_info(
        self, token: str, artist_ids: List[str]
    ) -> Dict[str, Any]:
        """Get information about specific artists."""
        if not artist_ids:
            return {"artists": []}

        artists = []
        for artist_id in artist_ids:
            url = f"{self._base_url}/v1/catalog/us/artists/{artist_id}"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                response_data = response.json()
                if "data" in response_data and response_data["data"]:
                    artist_data = response_data["data"][0]
                    attributes = artist_data.get("attributes", {})
                    
                    artists.append({
                        "id": artist_data.get("id"),
                        "name": attributes.get("name"),
                        "genres": attributes.get("genreNames", []),
                        "external_urls": {
                            "apple_music": attributes.get("url")
                        }
                    })
                    
            except requests.exceptions.HTTPError as err:
                logger.error(f"Failed to get artist {artist_id}: {err}")
                continue
            except requests.exceptions.RequestException as err:
                logger.error(f"Network error while getting artist {artist_id}: {err}")
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
        """Get user's saved albums with pagination.
        
        Note: Requires user authorization.
        """
        logger.warning("Apple Music user saved albums require user authorization")
        return {
            "albums": [],
            "total_albums": 0,
            "limit": limit,
            "offset": offset
        }

    def get_user_saved_albums(
        self, token: str, user_id: str
    ) -> Dict[str, Any]:
        """Get all user's saved albums.
        
        Note: Requires user authorization.
        """
        logger.warning("Apple Music user saved albums require user authorization")
        return {
            "albums": [],
            "user_albums": []
        }