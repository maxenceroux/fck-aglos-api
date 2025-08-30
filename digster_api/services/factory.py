"""Service factory functions."""

import os
from .streaming import StreamingServiceInterface, SpotifyController, AppleMusicController, DeezerController


def get_streaming_service(service_type: str = "spotify") -> StreamingServiceInterface:
    """Factory function to get the streaming service instance.
    
    Args:
        service_type: The type of streaming service ('spotify', 'apple_music', 'deezer')
    
    Returns:
        StreamingServiceInterface implementation
    """
    if service_type.lower() == "spotify":
        return SpotifyController(
            client_id=str(os.environ.get("SPOTIFY_CLIENT_ID")),
            client_secret=str(os.environ.get("SPOTIFY_CLIENT_SECRET")),
        )
    elif service_type.lower() == "apple_music":
        return AppleMusicController(
            client_id=str(os.environ.get("APPLE_MUSIC_TEAM_ID")),
            client_secret=str(os.environ.get("APPLE_MUSIC_KEY_ID")),
        )
    elif service_type.lower() == "deezer":
        return DeezerController(
            client_id=str(os.environ.get("DEEZER_CLIENT_ID")),
            client_secret=str(os.environ.get("DEEZER_CLIENT_SECRET")),
        )
    else:
        # Default to Spotify for backward compatibility
        return SpotifyController(
            client_id=str(os.environ.get("SPOTIFY_CLIENT_ID")),
            client_secret=str(os.environ.get("SPOTIFY_CLIENT_SECRET")),
        )