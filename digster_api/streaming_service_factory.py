"""Streaming service factory and utility functions."""

from typing import Dict, Any, Optional
from .spotify_controller import SpotifyController
from .deezer_controller import DeezerController
from .streaming_service_interface import StreamingServiceInterface


class StreamingServiceFactory:
    """Factory class for creating streaming service instances."""
    
    _services = {
        'spotify': SpotifyController,
        'deezer': DeezerController,
    }
    
    @classmethod
    def create_service(cls, service_name: str, client_id: str, client_secret: str) -> StreamingServiceInterface:
        """Create a streaming service instance."""
        if service_name not in cls._services:
            raise ValueError(f"Unsupported streaming service: {service_name}")
        
        return cls._services[service_name](client_id, client_secret)
    
    @classmethod
    def get_supported_services(cls) -> list:
        """Get list of supported streaming services."""
        return list(cls._services.keys())


def get_streaming_service(service_name: str = 'spotify') -> StreamingServiceInterface:
    """Get streaming service instance with default configuration.
    
    This is a convenience function that can be updated to read from config.
    """
    import os
    
    if service_name == 'spotify':
        client_id = os.environ.get('SPOTIFY_CLIENT_ID', '')
        client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET', '')
    elif service_name == 'deezer':
        client_id = os.environ.get('DEEZER_CLIENT_ID', '')
        client_secret = os.environ.get('DEEZER_CLIENT_SECRET', '')
    else:
        raise ValueError(f"Unsupported streaming service: {service_name}")
    
    return StreamingServiceFactory.create_service(service_name, client_id, client_secret)


def normalize_track_data(track_data: Dict[str, Any], service_name: str) -> Dict[str, Any]:
    """Normalize track data from different streaming services to a common format."""
    if service_name == 'spotify':
        return {
            'external_id': track_data.get('spotify_id'),
            'name': track_data.get('name'),
            'duration_ms': track_data.get('duration_ms'),
            'popularity': track_data.get('popularity'),
            'album_id': track_data.get('album_id'),
        }
    elif service_name == 'deezer':
        return {
            'external_id': track_data.get('deezer_id'),
            'name': track_data.get('name'),
            'duration_ms': track_data.get('duration_ms'),
            'popularity': track_data.get('popularity'),
            'album_id': track_data.get('album_id'),
        }
    else:
        # Return as-is for unknown services
        return track_data


def normalize_album_data(album_data: Dict[str, Any], service_name: str) -> Dict[str, Any]:
    """Normalize album data from different streaming services to a common format."""
    if service_name == 'spotify':
        return {
            'external_id': album_data.get('spotify_id'),
            'artist_id': album_data.get('artist_id'),
            'genres': album_data.get('genres'),
            'image_url': album_data.get('image_url'),
            'label': album_data.get('label'),
            'name': album_data.get('name'),
            'popularity': album_data.get('popularity'),
            'release_date': album_data.get('release_date'),
            'total_tracks': album_data.get('total_tracks'),
        }
    elif service_name == 'deezer':
        return {
            'external_id': album_data.get('deezer_id'),
            'artist_id': album_data.get('artist_id'),
            'genres': album_data.get('genres'),
            'image_url': album_data.get('image_url'),
            'label': album_data.get('label'),
            'name': album_data.get('name'),
            'popularity': album_data.get('popularity'),
            'release_date': album_data.get('release_date'),
            'total_tracks': album_data.get('total_tracks'),
        }
    else:
        # Return as-is for unknown services
        return album_data


def normalize_artist_data(artist_data: Dict[str, Any], service_name: str) -> Dict[str, Any]:
    """Normalize artist data from different streaming services to a common format."""
    if service_name == 'spotify':
        return {
            'external_id': artist_data.get('spotify_id'),
            'name': artist_data.get('name'),
            'popularity': artist_data.get('popularity'),
            'image_url': artist_data.get('image_url'),
            'genres': artist_data.get('genres', ''),
        }
    elif service_name == 'deezer':
        return {
            'external_id': artist_data.get('deezer_id'),
            'name': artist_data.get('name'),
            'popularity': artist_data.get('popularity'),
            'image_url': artist_data.get('image_url'),
            'genres': artist_data.get('genres', ''),
        }
    else:
        # Return as-is for unknown services
        return artist_data