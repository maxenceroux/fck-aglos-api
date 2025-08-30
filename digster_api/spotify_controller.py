import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional
    pass

from requests.auth import HTTPBasicAuth
import base64

from .streaming_service_interface import StreamingServiceInterface

# Configure logger
logger = logging.getLogger(__name__)


class SpotifyAPIError(Exception):
    """Custom exception for Spotify API errors."""
    pass


class SpotifyAuthenticationError(SpotifyAPIError):
    """Exception raised when authentication fails."""
    pass


class SpotifyController(StreamingServiceInterface):
    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self._base_url = "https://api.spotify.com"

    def get_unauth_token(self) -> str:
        """Get an unauthenticated token for API access."""
        url = "https://accounts.spotify.com/api/token"
        payload = "grant_type=client_credentials"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        try:
            response = requests.post(
                url,
                auth=HTTPBasicAuth(self.client_id, self.client_secret),
                headers=headers,
                data=payload,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to get unauthenticated token: {err}")
            raise SpotifyAuthenticationError(f"Failed to get unauthenticated token: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting unauthenticated token: {err}")
            raise SpotifyAPIError(f"Network error while getting unauthenticated token: {err}") from err
            
        token = response.json().get("access_token")
        if not token:
            logger.error("No access token received in response")
            raise SpotifyAuthenticationError("No access token received in response")
            
        return token

    def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh the access token using a refresh token."""
        auth_url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic "
            + base64.b64encode(
                (self.client_id + ":" + self.client_secret).encode()
            ).decode(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        
        try:
            response = requests.post(auth_url, headers=headers, data=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to refresh access token: {err}")
            raise SpotifyAuthenticationError(f"Failed to refresh access token: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while refreshing access token: {err}")
            raise SpotifyAPIError(f"Network error while refreshing access token: {err}") from err
            
        token = response.json().get("access_token")
        if not token:
            logger.error("No access token received in refresh response")
            raise SpotifyAuthenticationError("No access token received in refresh response")
            
        return token

    def get_current_play(self, token: str) -> Dict[str, Any]:
        """Get the currently playing track for the user."""
        url = f"{self._base_url}/v1/me/player"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to get current play: {err}")
            raise SpotifyAPIError(f"Failed to get current play: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting current play: {err}")
            raise SpotifyAPIError(f"Network error while getting current play: {err}") from err
            
        response_data = response.json()
        if not response_data or not response_data.get("item"):
            logger.warning("No currently playing track found")
            return {}
            
        current_play = {
            "listened_at": response_data.get("timestamp"),
            "track_id": response_data.get("item", {}).get("id")
        }
        return current_play

    def save_album(
        self, tokens: Dict[str, Any], album_id: str
    ) -> Dict[str, Any]:
        """Save an album to the user's library."""
        url = f"{self._base_url}/v1/me/albums"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {tokens['access_token']}",
        }
        data = {"ids": [album_id]}

        try:
            response = requests.put(url, headers=headers, json=data)
            if response.status_code == 401:
                logger.info("Access token expired, refreshing tokens...")
                tokens["access_token"] = self.refresh_access_token(
                    tokens["refresh_token"]
                )
                return self.save_album(tokens, album_id)
            response.raise_for_status()
            return {"status": "success", "message": "Album saved successfully"}
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to save album {album_id}: {err}")
            raise SpotifyAPIError(f"Failed to save album {album_id}: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while saving album {album_id}: {err}")
            raise SpotifyAPIError(f"Network error while saving album {album_id}: {err}") from err

    def get_user_info(self, token: str) -> Dict[str, Any]:
        """Get user information."""
        url = f"{self._base_url}/v1/me"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to get user info: {err}")
            raise SpotifyAPIError(f"Failed to get user info: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting user info: {err}")
            raise SpotifyAPIError(f"Network error while getting user info: {err}") from err
            
        response_data = response.json()
        current_user = {
            "id": response_data.get("id"),
            "display_name": response_data.get("display_name"),
            "email": response_data.get("email"),
            "country": response_data.get("country"),
            "image_url": (
                response_data.get("images", [{}])[-1].get("url")
                if response_data.get("images")
                else None
            )
        }
        return current_user

    def get_recently_played(
        self,
        token: str,
        url: Optional[str] = None,
        after: Optional[int] = None,
        limit: Optional[int] = 50,
    ) -> Dict[str, Any]:
        """Get recently played tracks."""
        if not url:
            if after:
                url = (
                    f"{self._base_url}/v1/me/player/recently-played"
                    f"?limit={limit}&after={after}"
                )
            else:
                url = (
                    f"{self._base_url}/v1/me/player/recently-played"
                    f"?limit={limit}"
                )
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to get recently played tracks: {err}")
            raise SpotifyAPIError(f"Failed to get recently played tracks: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting recently played tracks: {err}")
            raise SpotifyAPIError(f"Network error while getting recently played tracks: {err}") from err
            
        response_data = response.json()
        if not response_data.get("items"):
            return {"message": f"no tracks played after {after}"}
            
        recently_played_tracks = []
        for track in response_data.get("items", []):
            recently_played_tracks.append(
                {
                    "listened_at": datetime.fromisoformat(
                        track.get("played_at", "")[:-1]
                    ),
                    "track_id": track.get("track", {}).get("id"),
                }
            )
        
        recently_played_tracks.reverse()
        results = {
            "next_url": response_data.get("next"),
            "recently_played": recently_played_tracks
        }
        return results

    def get_tracks_info(
        self, token: str, track_ids: List[str]
    ) -> Dict[str, Any]:
        """Get information about specific tracks."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        params = {"ids": ",".join(track_ids)}
        url = f"{self._base_url}/v1/tracks"
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to get tracks info: {err}")
            raise SpotifyAPIError(f"Failed to get tracks info: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting tracks info: {err}")
            raise SpotifyAPIError(f"Network error while getting tracks info: {err}") from err
            
        response_data = response.json()
        if not response_data.get("tracks"):
            return {"message": "IDs corresponding to no tracks"}
            
        tracks_info = []
        for track in response_data.get("tracks", []):
            tracks_info.append(
                {
                    "spotify_id": track.get("id"),
                    "name": track.get("name"),
                    "duration_ms": track.get("duration_ms"),
                    "popularity": track.get("popularity"),
                    "album_id": track.get("album", {}).get("id"),
                }
            )
        
        return {"tracks_info": tracks_info}

    def get_tracks_attributes(
        self, token: str, track_ids: List[str]
    ) -> Dict[str, Any]:
        """Get audio features/attributes for specific tracks."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        params = {"ids": ",".join(track_ids)}
        url = f"{self._base_url}/v1/audio-features"
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to get tracks attributes: {err}")
            raise SpotifyAPIError(f"Failed to get tracks attributes: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting tracks attributes: {err}")
            raise SpotifyAPIError(f"Network error while getting tracks attributes: {err}") from err
            
        response_data = response.json()
        if not response_data.get("audio_features"):
            return {"message": "IDs corresponding to no tracks"}
            
        tracks_audio_features = []
        for track in response_data.get("audio_features", []):
            if track:  # track can be None for invalid IDs
                tracks_audio_features.append(
                    {
                        "spotify_id": track.get("id"),
                        "danceability": track.get("danceability"),
                        "energy": track.get("energy"),
                        "key": track.get("key"),
                        "loudness": track.get("loudness"),
                        "mode": track.get("mode"),
                        "speechiness": track.get("speechiness"),
                        "acousticness": track.get("acousticness"),
                        "instrumentalness": track.get("instrumentalness"),
                        "liveness": track.get("liveness"),
                        "valence": track.get("valence"),
                        "tempo": track.get("tempo"),
                    }
                )
        
        return {"audio_features": tracks_audio_features}

    def get_albums_info(
        self, token: str, album_ids: List[str]
    ) -> Dict[str, Any]:
        """Get information about specific albums."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        params = {"ids": ",".join(album_ids)}
        url = f"{self._base_url}/v1/albums"
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to get albums info: {err}")
            raise SpotifyAPIError(f"Failed to get albums info: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting albums info: {err}")
            raise SpotifyAPIError(f"Network error while getting albums info: {err}") from err
            
        response_data = response.json()
        if not response_data.get("albums"):
            return {"message": "IDs corresponding to no albums"}
            
        albums = []
        for album in response_data.get("albums", []):
            if album:  # album can be None for invalid IDs
                albums.append(
                    {
                        "spotify_id": album.get("id"),
                        "artist_id": album.get("artists", [{}])[0].get("id"),
                        "genres": " - ".join(album.get("genres", [])),
                        "image_url": album.get("images", [{}])[0].get("url") if album.get("images") else None,
                        "label": album.get("label"),
                        "name": album.get("name"),
                        "popularity": album.get("popularity"),
                        "release_date": album.get("release_date"),
                        "total_tracks": album.get("total_tracks"),
                    }
                )
        
        return {"albums": albums}

    def get_artists_info(
        self, token: str, artist_ids: List[str]
    ) -> Dict[str, Any]:
        """Get information about specific artists."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        params = {"ids": ",".join(artist_ids)}
        url = f"{self._base_url}/v1/artists"
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to get artists info: {err}")
            raise SpotifyAPIError(f"Failed to get artists info: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting artists info: {err}")
            raise SpotifyAPIError(f"Network error while getting artists info: {err}") from err
            
        response_data = response.json()
        if not response_data.get("artists"):
            return {"message": "IDs corresponding to no artists"}
            
        artists = []
        for artist in response_data.get("artists", []):
            if artist:  # artist can be None for invalid IDs
                artists.append(
                    {
                        "spotify_id": artist.get("id"),
                        "genres": " - ".join(artist.get("genres", [])),
                        "image_url": (
                            artist.get("images", [{}])[0].get("url")
                            if artist.get("images")
                            else None
                        ),
                        "name": artist.get("name"),
                        "followers": artist.get("followers", {}).get("total"),
                        "popularity": artist.get("popularity"),
                    }
                )
        
        return {"artists": artists}

    def get_user_saved_albums_limit(
        self,
        tokens: Dict[str, Any],
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get user's saved albums with pagination."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {tokens['access_token']}",
        }
        params = {"limit": limit, "offset": offset}
        url = f"{self._base_url}/v1/me/albums"
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 401:
                logger.info("Access token expired, refreshing tokens...")
                tokens["access_token"] = self.refresh_access_token(
                    tokens["refresh_token"]
                )
                return self.get_user_saved_albums_limit(tokens, limit, offset)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Error getting user saved albums: {err}")
            raise SpotifyAPIError(f"Error getting user saved albums: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting user saved albums: {err}")
            raise SpotifyAPIError(f"Network error while getting user saved albums: {err}") from err
            
        response_data = response.json()
        albums = []
        
        if response_data.get("items"):
            for item in response_data.get("items", []):
                album_data = item.get("album", {})
                artists = album_data.get("artists", [{}])
                images = album_data.get("images", [{}])
                external_ids = album_data.get("external_ids", {})
                
                single_album = {
                    "spotify_id": album_data.get("id"),
                    "type": album_data.get("album_type"),
                    "artist_spotify_id": artists[0].get("id") if artists else None,
                    "artist_name": artists[0].get("name") if artists else None,
                    "upc_id": external_ids.get("upc"),
                    "label": album_data.get("label"),
                    "name": album_data.get("name"),
                    "release_date": album_data.get("release_date"),
                    "image_url": images[0].get("url") if images else None,
                    "genres": " - ".join(album_data.get("genres", [])),
                    "total_tracks": album_data.get("total_tracks"),
                    "popularity": album_data.get("popularity"),
                    "created_at": datetime.now(),
                    "added_at": item.get("added_at"),
                }
                albums.append(single_album)
        
        return {
            "albums": albums,
            "total_albums": response_data.get("total")
        }

    def get_user_saved_albums(
        self, token: str, user_spotify_id: str
    ) -> Dict[str, Any]:
        """Get all user's saved albums."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        params = {"limit": 50, "offset": 0}
        url = f"{self._base_url}/v1/me/albums"
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(f"Failed to get user saved albums: {err}")
            raise SpotifyAPIError(f"Failed to get user saved albums: {err}") from err
        except requests.exceptions.RequestException as err:
            logger.error(f"Network error while getting user saved albums: {err}")
            raise SpotifyAPIError(f"Network error while getting user saved albums: {err}") from err
            
        albums = []
        user_albums = []
        
        def _process_album_item(item: Dict[str, Any]) -> None:
            """Helper function to process a single album item."""
            album_data = item.get("album", {})
            artists = album_data.get("artists", [{}])
            images = album_data.get("images", [{}])
            external_ids = album_data.get("external_ids", {})
            
            single_album = {
                "spotify_id": album_data.get("id"),
                "type": album_data.get("album_type"),
                "artist_spotify_id": artists[0].get("id") if artists else None,
                "artist_name": artists[0].get("name") if artists else None,
                "upc_id": external_ids.get("upc"),
                "label": album_data.get("label"),
                "name": album_data.get("name"),
                "release_date": album_data.get("release_date"),
                "image_url": images[0].get("url") if images else None,
                "genres": " - ".join(album_data.get("genres", [])),
                "total_tracks": album_data.get("total_tracks"),
                "popularity": album_data.get("popularity"),
                "created_at": datetime.now(),
            }
            
            single_user_album = {
                "user_spotify_id": user_spotify_id,
                "album_spotify_id": album_data.get("id"),
                "added_at": item.get("added_at"),
                "created_at": datetime.now(),
            }
            
            albums.append(single_album)
            user_albums.append(single_user_album)
        
        # Process all items across all pages
        response_data = response.json()
        current_url = url
        
        while True:
            if response_data.get("items"):
                for item in response_data.get("items", []):
                    _process_album_item(item)
            
            # Check if there's a next page
            next_url = response_data.get("next")
            if not next_url:
                break
                
            # Get next page
            try:
                response = requests.get(next_url, headers=headers)
                response.raise_for_status()
                response_data = response.json()
            except requests.exceptions.RequestException as err:
                logger.error(f"Error fetching next page of albums: {err}")
                break  # Don't fail completely, just stop pagination
        
        return {
            "albums": albums,
            "user_albums": user_albums
        }
