import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import base64

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional
    pass

from .streaming_service_interface import StreamingServiceInterface

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
        
        Note: Deezer API doesn't require authentication for most read operations.
        This method returns an empty string as a placeholder since many operations
        can be performed without authentication.
        """
        # Deezer API allows many operations without authentication
        # For operations that require auth, we'll use the user's access token directly
        logger.info("Deezer API operations can be performed without app-level authentication")
        return ""

    def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh the access token using a refresh token.
        
        Note: Deezer doesn't use refresh tokens in the same way as Spotify.
        Deezer access tokens have longer expiration times (typically 1 hour to several days).
        """
        # Deezer doesn't have a refresh token mechanism like Spotify
        # Access tokens are refreshed through the OAuth flow
        logger.warning("Deezer doesn't support refresh tokens. Re-authentication required.")
        raise DeezerAuthenticationError("Deezer doesn't support refresh tokens. Please re-authenticate.")

    def get_current_play(self, token: str) -> Dict[str, Any]:
        """Get the currently playing track for the user.
        
        Note: Deezer API doesn't provide a "currently playing" endpoint.
        This would typically require integration with Deezer's player or real-time APIs.
        """
        logger.warning("Deezer API doesn't provide currently playing track information")
        return {}

    def save_album(self, tokens: Dict[str, Any], album_id: str) -> Dict[str, Any]:
        """Save an album to the user's library."""
        access_token = tokens.get("access_token")
        if not access_token:
            raise DeezerAuthenticationError("Access token required for saving albums")

        url = f"{self._base_url}/user/me/albums"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"album_id": album_id}
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to save album {album_id}: {err}")
            raise DeezerAPIError(f"Failed to save album {album_id}: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while saving album {album_id}: {err}")
            raise DeezerAPIError(f"Network error while saving album {album_id}: {err}") from err
            
        return {"status": "success", "album_id": album_id}

    def get_user_info(self, token: str) -> Dict[str, Any]:
        """Get user information."""
        url = f"{self._base_url}/user/me"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to get user info: {err}")
            raise DeezerAPIError(f"Failed to get user info: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting user info: {err}")
            raise DeezerAPIError(f"Network error while getting user info: {err}") from err
            
        response_data = response.json()
        
        user_info = {
            "id": str(response_data.get("id")),
            "display_name": response_data.get("name"),
            "email": response_data.get("email"),
            "country": response_data.get("country"),
            "image_url": response_data.get("picture_medium"),
            "external_urls": {
                "deezer": response_data.get("link")
            }
        }
        
        return user_info

    def get_recently_played(
        self,
        token: str,
        url: Optional[str] = None,
        after: Optional[int] = None,
        limit: Optional[int] = 50,
    ) -> Dict[str, Any]:
        """Get recently played tracks.
        
        Note: Deezer doesn't have a direct "recently played" endpoint.
        This would need to be implemented through listening history or user activity.
        """
        logger.warning("Deezer API doesn't provide recently played tracks directly")
        return {
            "next_url": None,
            "recently_played": []
        }

    def get_tracks_info(self, token: str, track_ids: List[str]) -> Dict[str, Any]:
        """Get information about specific tracks."""
        if not track_ids:
            return {"tracks_info": []}
            
        tracks_info = []
        
        # Deezer API doesn't support batch requests for tracks
        # We need to make individual requests for each track
        for track_id in track_ids:
            url = f"{self._base_url}/track/{track_id}"
            
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                track_data = response.json()
                
                if "error" not in track_data:
                    track_info = {
                        "deezer_id": track_data.get("id"),
                        "name": track_data.get("title"),
                        "duration_ms": track_data.get("duration", 0) * 1000,  # Deezer returns seconds
                        "popularity": track_data.get("rank"),
                        "album_id": track_data.get("album", {}).get("id"),
                        "artist_name": track_data.get("artist", {}).get("name"),
                        "preview_url": track_data.get("preview"),
                        "external_urls": {
                            "deezer": track_data.get("link")
                        }
                    }
                    tracks_info.append(track_info)
                    
            except requests.exceptions.RequestException as err:
                logger.error(f"Failed to get info for track {track_id}: {err}")
                continue
                
        return {"tracks_info": tracks_info}

    def get_tracks_attributes(self, token: str, track_ids: List[str]) -> Dict[str, Any]:
        """Get audio features/attributes for specific tracks.
        
        Note: Deezer API doesn't provide audio features like Spotify.
        This would return basic track information instead.
        """
        logger.warning("Deezer API doesn't provide audio features like Spotify")
        return self.get_tracks_info(token, track_ids)

    def get_albums_info(self, token: str, album_ids: List[str]) -> Dict[str, Any]:
        """Get information about specific albums."""
        if not album_ids:
            return {"albums_info": []}
            
        albums_info = []
        
        for album_id in album_ids:
            url = f"{self._base_url}/album/{album_id}"
            
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                album_data = response.json()
                
                if "error" not in album_data:
                    album_info = {
                        "deezer_id": album_data.get("id"),
                        "name": album_data.get("title"),
                        "artist_name": album_data.get("artist", {}).get("name"),
                        "artist_id": album_data.get("artist", {}).get("id"),
                        "release_date": album_data.get("release_date"),
                        "total_tracks": album_data.get("nb_tracks"),
                        "image_url": album_data.get("cover_medium"),
                        "genres": ", ".join([genre.get("name", "") for genre in album_data.get("genres", {}).get("data", [])]),
                        "label": album_data.get("label"),
                        "upc": album_data.get("upc"),
                        "external_urls": {
                            "deezer": album_data.get("link")
                        }
                    }
                    albums_info.append(album_info)
                    
            except requests.exceptions.RequestException as err:
                logger.error(f"Failed to get info for album {album_id}: {err}")
                continue
                
        return {"albums_info": albums_info}

    def get_artists_info(self, token: str, artist_ids: List[str]) -> Dict[str, Any]:
        """Get information about specific artists."""
        if not artist_ids:
            return {"artists_info": []}
            
        artists_info = []
        
        for artist_id in artist_ids:
            url = f"{self._base_url}/artist/{artist_id}"
            
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                artist_data = response.json()
                
                if "error" not in artist_data:
                    artist_info = {
                        "deezer_id": artist_data.get("id"),
                        "name": artist_data.get("name"),
                        "nb_fans": artist_data.get("nb_fan"),
                        "image_url": artist_data.get("picture_medium"),
                        "external_urls": {
                            "deezer": artist_data.get("link")
                        }
                    }
                    artists_info.append(artist_info)
                    
            except requests.exceptions.RequestException as err:
                logger.error(f"Failed to get info for artist {artist_id}: {err}")
                continue
                
        return {"artists_info": artists_info}

    def get_user_saved_albums_limit(
        self,
        tokens: Dict[str, Any],
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get user's saved albums with pagination."""
        access_token = tokens.get("access_token")
        if not access_token:
            raise DeezerAuthenticationError("Access token required for getting saved albums")

        url = f"{self._base_url}/user/me/albums"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"limit": limit, "index": offset}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Error getting user saved albums: {err}")
            raise DeezerAPIError(f"Error getting user saved albums: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting user saved albums: {err}")
            raise DeezerAPIError(f"Network error while getting user saved albums: {err}") from err
            
        response_data = response.json()
        albums = []
        
        if response_data.get("data"):
            for album_data in response_data.get("data", []):
                album = {
                    "deezer_id": album_data.get("id"),
                    "name": album_data.get("title"),
                    "artist_name": album_data.get("artist", {}).get("name"),
                    "artist_id": album_data.get("artist", {}).get("id"),
                    "release_date": album_data.get("release_date"),
                    "total_tracks": album_data.get("nb_tracks"),
                    "image_url": album_data.get("cover_medium"),
                    "type": album_data.get("record_type"),
                    "external_urls": {
                        "deezer": album_data.get("link")
                    },
                    "created_at": datetime.now(),
                }
                albums.append(album)
                
        return {
            "albums": albums,
            "total": response_data.get("total", 0),
            "next": response_data.get("next"),
            "prev": response_data.get("prev")
        }

    def get_user_saved_albums(self, token: str, user_id: str) -> Dict[str, Any]:
        """Get all user's saved albums."""
        albums = []
        user_albums = []
        offset = 0
        limit = 50
        
        # Create tokens dict for compatibility with the limit method
        tokens = {"access_token": token}
        
        while True:
            try:
                response = self.get_user_saved_albums_limit(tokens, limit, offset)
                batch_albums = response.get("albums", [])
                
                if not batch_albums:
                    break
                    
                albums.extend(batch_albums)
                
                # Create user_albums entries for database compatibility
                for album in batch_albums:
                    user_albums.append({
                        "user_id": user_id,
                        "album_id": album.get("deezer_id"),
                        "created_at": album.get("created_at", datetime.now())
                    })
                
                # Check if we have more data
                if not response.get("next"):
                    break
                    
                offset += limit
                
            except Exception as err:
                logger.error(f"Error in pagination for user {user_id}: {err}")
                break
        
        return {
            "albums": albums,
            "user_albums": user_albums
        }