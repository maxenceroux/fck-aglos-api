"""Abstract interface for streaming service implementations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class StreamingServiceInterface(ABC):
    """Abstract base class defining the interface for streaming services."""

    @abstractmethod
    def __init__(self, client_id: str, client_secret: str) -> None:
        """Initialize the streaming service client."""
        pass

    @abstractmethod
    def get_unauth_token(self) -> str:
        """Get an unauthenticated token for API access."""
        pass

    @abstractmethod
    def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh the access token using a refresh token."""
        pass

    @abstractmethod
    def get_current_play(self, token: str) -> Dict[str, Any]:
        """Get the currently playing track for the user."""
        pass

    @abstractmethod
    def save_album(
        self, tokens: Dict[str, Any], album_id: str
    ) -> Dict[str, Any]:
        """Save an album to the user's library."""
        pass

    @abstractmethod
    def get_user_info(self, token: str) -> Dict[str, Any]:
        """Get user information."""
        pass

    @abstractmethod
    def get_recently_played(
        self,
        token: str,
        url: Optional[str] = None,
        after: Optional[int] = None,
        limit: Optional[int] = 50,
    ) -> Dict[str, Any]:
        """Get recently played tracks."""
        pass

    @abstractmethod
    def get_tracks_info(
        self, token: str, track_ids: List[str]
    ) -> Dict[str, Any]:
        """Get information about specific tracks."""
        pass

    @abstractmethod
    def get_tracks_attributes(
        self, token: str, track_ids: List[str]
    ) -> Dict[str, Any]:
        """Get audio features/attributes for specific tracks."""
        pass

    @abstractmethod
    def get_albums_info(
        self, token: str, album_ids: List[str]
    ) -> Dict[str, Any]:
        """Get information about specific albums."""
        pass

    @abstractmethod
    def get_artists_info(
        self, token: str, artist_ids: List[str]
    ) -> Dict[str, Any]:
        """Get information about specific artists."""
        pass

    @abstractmethod
    def get_user_saved_albums_limit(
        self,
        tokens: Dict[str, Any],
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get user's saved albums with pagination."""
        pass

    @abstractmethod
    def get_user_saved_albums(
        self, token: str, user_id: str
    ) -> Dict[str, Any]:
        """Get all user's saved albums."""
        pass