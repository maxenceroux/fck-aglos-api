"""Tests for the streaming service interface abstraction."""

import os
from unittest.mock import Mock, patch

import pytest

from digster_api.streaming_service_interface import StreamingServiceInterface
from digster_api.spotify_controller import SpotifyController
from digster_api.deezer_controller import DeezerController


def test_deezer_controller_implements_interface():
    """Test that DeezerController correctly implements StreamingServiceInterface."""
    # Test instantiation
    controller = DeezerController(client_id="test_id", client_secret="test_secret")
    
    # Verify it's an instance of the interface
    assert isinstance(controller, StreamingServiceInterface)
    
    # Verify it has all required attributes
    assert hasattr(controller, 'get_unauth_token')
    assert hasattr(controller, 'refresh_access_token')
    assert hasattr(controller, 'get_current_play')
    assert hasattr(controller, 'save_album')
    assert hasattr(controller, 'get_user_info')
    assert hasattr(controller, 'get_recently_played')
    assert hasattr(controller, 'get_tracks_info')
    assert hasattr(controller, 'get_tracks_attributes')
    assert hasattr(controller, 'get_albums_info')
    assert hasattr(controller, 'get_artists_info')
    assert hasattr(controller, 'get_user_saved_albums_limit')
    assert hasattr(controller, 'get_user_saved_albums')


def test_spotify_controller_implements_interface():
    """Test that SpotifyController correctly implements StreamingServiceInterface."""
    # Test instantiation
    controller = SpotifyController(client_id="test_id", client_secret="test_secret")
    
    # Verify it's an instance of the interface
    assert isinstance(controller, StreamingServiceInterface)
    
    # Verify it has all required attributes
    assert hasattr(controller, 'get_unauth_token')
    assert hasattr(controller, 'refresh_access_token')
    assert hasattr(controller, 'get_current_play')
    assert hasattr(controller, 'save_album')
    assert hasattr(controller, 'get_user_info')
    assert hasattr(controller, 'get_recently_played')
    assert hasattr(controller, 'get_tracks_info')
    assert hasattr(controller, 'get_tracks_attributes')
    assert hasattr(controller, 'get_albums_info')
    assert hasattr(controller, 'get_artists_info')
    assert hasattr(controller, 'get_user_saved_albums_limit')
    assert hasattr(controller, 'get_user_saved_albums')


def test_interface_inheritance():
    """Test that the interface methods are properly abstract."""
    # Test that we cannot instantiate the interface directly
    with pytest.raises(TypeError):
        StreamingServiceInterface(client_id="test", client_secret="test")


def test_factory_function():
    """Test the factory function in main.py."""
    from digster_api.main import get_streaming_service
    
    with patch.dict(os.environ, {
        'SPOTIFY_CLIENT_ID': 'test_client_id',
        'SPOTIFY_CLIENT_SECRET': 'test_client_secret'
    }):
        service = get_streaming_service()
        assert isinstance(service, StreamingServiceInterface)
        assert isinstance(service, SpotifyController)
        assert service.client_id == 'test_client_id'
        assert service.client_secret == 'test_client_secret'


def test_bg_tasks_factory_function():
    """Test the factory function in bg_tasks.py."""
    from digster_api.bg_tasks import get_streaming_service as bg_get_streaming_service
    
    with patch.dict(os.environ, {
        'SPOTIFY_CLIENT_ID': 'test_client_id', 
        'SPOTIFY_CLIENT_SECRET': 'test_client_secret'
    }):
        service = bg_get_streaming_service()
        assert isinstance(service, StreamingServiceInterface)
        assert isinstance(service, SpotifyController)