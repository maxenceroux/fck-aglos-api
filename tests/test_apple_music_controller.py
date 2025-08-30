"""Tests for the Apple Music streaming service implementation."""

import pytest
from unittest.mock import Mock, patch

from digster_api.apple_music_controller import (
    AppleMusicController,
    AppleMusicAuthenticationError,
    AppleMusicAPIError,
)
from digster_api.streaming_service_interface import StreamingServiceInterface


def test_apple_music_controller_implements_interface():
    """Test that AppleMusicController correctly implements
    StreamingServiceInterface."""
    # Test instantiation
    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    # Verify it's an instance of the interface
    assert isinstance(controller, StreamingServiceInterface)

    # Verify it has all required attributes
    assert hasattr(controller, "get_unauth_token")
    assert hasattr(controller, "refresh_access_token")
    assert hasattr(controller, "get_current_play")
    assert hasattr(controller, "save_album")
    assert hasattr(controller, "get_user_info")
    assert hasattr(controller, "get_recently_played")
    assert hasattr(controller, "get_tracks_info")
    assert hasattr(controller, "get_tracks_attributes")
    assert hasattr(controller, "get_albums_info")
    assert hasattr(controller, "get_artists_info")
    assert hasattr(controller, "get_user_saved_albums_limit")
    assert hasattr(controller, "get_user_saved_albums")


def test_apple_music_controller_initialization():
    """Test AppleMusicController initialization."""
    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    assert controller.team_id == "test_team_id"
    assert controller.key_id == "test_key_id"
    assert controller._base_url == "https://api.music.apple.com"


def test_get_unauth_token():
    """Test get_unauth_token method."""
    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    token = controller.get_unauth_token()
    
    # Should return a JWT-like token (3 parts separated by dots)
    assert isinstance(token, str)
    assert len(token.split('.')) == 3  # JWT format


def test_refresh_access_token():
    """Test refresh_access_token method."""
    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    # For Apple Music, this should generate a new JWT token
    token = controller.refresh_access_token("dummy_refresh_token")
    
    assert isinstance(token, str)
    assert len(token.split('.')) == 3  # JWT format


def test_get_current_play():
    """Test get_current_play method."""
    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    result = controller.get_current_play("dummy_token")
    
    # Apple Music doesn't support current playback without user auth
    assert result == {}


def test_save_album():
    """Test save_album method."""
    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    result = controller.save_album({"access_token": "dummy"}, "album123")
    
    # Should indicate that user authorization is required
    assert result["status"] == "error"
    assert "user authorization" in result["message"]


def test_get_user_info():
    """Test get_user_info method."""
    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    result = controller.get_user_info("dummy_token")
    
    # Should return placeholder user info
    assert "id" in result
    assert result["id"] == "apple_music_user"


def test_get_recently_played():
    """Test get_recently_played method."""
    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    result = controller.get_recently_played("dummy_token")
    
    # Should return empty tracks list
    assert "tracks" in result
    assert result["tracks"] == []


@patch('digster_api.apple_music_controller.requests.get')
def test_get_tracks_info_success(mock_get):
    """Test get_tracks_info method with successful response."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "data": [
            {
                "id": "track123",
                "attributes": {
                    "name": "Test Song",
                    "artistName": "Test Artist",
                    "albumName": "Test Album",
                    "durationInMillis": 180000,
                    "previews": [{"url": "https://preview.url"}],
                    "url": "https://music.apple.com/track"
                }
            }
        ]
    }
    mock_get.return_value = mock_response

    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    result = controller.get_tracks_info("dummy_token", ["track123"])
    
    assert "tracks" in result
    assert len(result["tracks"]) == 1
    assert result["tracks"][0]["id"] == "track123"
    assert result["tracks"][0]["name"] == "Test Song"


def test_get_tracks_info_empty_list():
    """Test get_tracks_info method with empty track list."""
    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    result = controller.get_tracks_info("dummy_token", [])
    
    assert result == {"tracks": []}


def test_get_tracks_attributes():
    """Test get_tracks_attributes method."""
    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    result = controller.get_tracks_attributes("dummy_token", ["track123"])
    
    # Should return placeholder audio features
    assert "audio_features" in result
    assert len(result["audio_features"]) == 1
    assert result["audio_features"][0]["id"] == "track123"


@patch('digster_api.apple_music_controller.requests.get')
def test_get_albums_info_success(mock_get):
    """Test get_albums_info method with successful response."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "data": [
            {
                "id": "album123",
                "attributes": {
                    "name": "Test Album",
                    "artistName": "Test Artist",
                    "releaseDate": "2021-01-01",
                    "trackCount": 10,
                    "genreNames": ["Pop"],
                    "artwork": {"url": "https://artwork.url"},
                    "url": "https://music.apple.com/album"
                }
            }
        ]
    }
    mock_get.return_value = mock_response

    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    result = controller.get_albums_info("dummy_token", ["album123"])
    
    assert "albums" in result
    assert len(result["albums"]) == 1
    assert result["albums"][0]["id"] == "album123"
    assert result["albums"][0]["name"] == "Test Album"


def test_get_albums_info_empty_list():
    """Test get_albums_info method with empty album list."""
    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    result = controller.get_albums_info("dummy_token", [])
    
    assert result == {"albums": []}


@patch('digster_api.apple_music_controller.requests.get')
def test_get_artists_info_success(mock_get):
    """Test get_artists_info method with successful response."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "data": [
            {
                "id": "artist123",
                "attributes": {
                    "name": "Test Artist",
                    "genreNames": ["Pop", "Rock"],
                    "url": "https://music.apple.com/artist"
                }
            }
        ]
    }
    mock_get.return_value = mock_response

    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    result = controller.get_artists_info("dummy_token", ["artist123"])
    
    assert "artists" in result
    assert len(result["artists"]) == 1
    assert result["artists"][0]["id"] == "artist123"
    assert result["artists"][0]["name"] == "Test Artist"


def test_get_artists_info_empty_list():
    """Test get_artists_info method with empty artist list."""
    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    result = controller.get_artists_info("dummy_token", [])
    
    assert result == {"artists": []}


def test_get_user_saved_albums_limit():
    """Test get_user_saved_albums_limit method."""
    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    result = controller.get_user_saved_albums_limit(
        {"access_token": "dummy"}, limit=25, offset=10
    )
    
    # Should return empty result with pagination info
    assert result["albums"] == []
    assert result["total_albums"] == 0
    assert result["limit"] == 25
    assert result["offset"] == 10


def test_get_user_saved_albums():
    """Test get_user_saved_albums method."""
    controller = AppleMusicController(
        client_id="test_team_id", client_secret="test_key_id"
    )

    result = controller.get_user_saved_albums("dummy_token", "user123")
    
    # Should return empty albums
    assert result["albums"] == []
    assert result["user_albums"] == []