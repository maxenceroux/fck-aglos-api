"""Streaming service clients."""

from .interface import StreamingServiceInterface
from .spotify_client import SpotifyController
from .deezer_client import DeezerController
from .apple_music_client import AppleMusicController

__all__ = [
    "StreamingServiceInterface",
    "SpotifyController", 
    "DeezerController",
    "AppleMusicController",
]