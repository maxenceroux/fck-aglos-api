"""Tests for the Deezer controller implementation."""

import os
from unittest.mock import Mock, patch, MagicMock
import requests

import pytest

from digster_api.streaming_service_interface import StreamingServiceInterface
from digster_api.deezer_controller import DeezerController, DeezerAPIError, DeezerAuthenticationError


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


def test_deezer_controller_initialization():
    """Test DeezerController initialization."""
    client_id = "test_client_id"
    client_secret = "test_client_secret"
    
    controller = DeezerController(client_id=client_id, client_secret=client_secret)
    
    assert controller.client_id == client_id
    assert controller.client_secret == client_secret
    assert controller._base_url == "https://api.deezer.com"


def test_get_unauth_token():
    """Test getting unauthenticated token (Deezer doesn't require it)."""
    controller = DeezerController("test_id", "test_secret")
    token = controller.get_unauth_token()
    assert token == ""


def test_refresh_access_token_raises_error():
    """Test that refresh_access_token raises appropriate error."""
    controller = DeezerController("test_id", "test_secret")
    
    with pytest.raises(DeezerAuthenticationError):
        controller.refresh_access_token("dummy_refresh_token")


def test_get_current_play_returns_empty():
    """Test that get_current_play returns empty dict (not supported by Deezer API)."""
    controller = DeezerController("test_id", "test_secret")
    result = controller.get_current_play("test_token")
    assert result == {}


def test_get_recently_played_returns_empty():
    """Test that get_recently_played returns empty structure (not supported by Deezer API)."""
    controller = DeezerController("test_id", "test_secret")
    result = controller.get_recently_played("test_token")
    
    assert "next_url" in result
    assert "recently_played" in result
    assert result["recently_played"] == []


@patch('digster_api.deezer_controller.requests.post')
def test_save_album_success(mock_post):
    """Test saving an album successfully."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    controller = DeezerController("test_id", "test_secret")
    tokens = {"access_token": "test_token"}
    album_id = "12345"
    
    result = controller.save_album(tokens, album_id)
    
    assert result["status"] == "success"
    assert result["album_id"] == album_id
    mock_post.assert_called_once()


def test_save_album_no_token():
    """Test saving album without access token raises error."""
    controller = DeezerController("test_id", "test_secret")
    tokens = {}  # No access token
    
    with pytest.raises(DeezerAuthenticationError):
        controller.save_album(tokens, "12345")


@patch('digster_api.deezer_controller.requests.get')
def test_get_user_info_success(mock_get):
    """Test getting user info successfully."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "id": 123456,
        "name": "Test User",
        "email": "test@example.com",
        "country": "US",
        "picture_medium": "http://example.com/picture.jpg",
        "link": "http://deezer.com/user/123456"
    }
    mock_get.return_value = mock_response
    
    controller = DeezerController("test_id", "test_secret")
    result = controller.get_user_info("test_token")
    
    assert result["id"] == "123456"
    assert result["display_name"] == "Test User"
    assert result["email"] == "test@example.com"
    assert result["country"] == "US"
    assert result["image_url"] == "http://example.com/picture.jpg"
    assert result["external_urls"]["deezer"] == "http://deezer.com/user/123456"


@patch('digster_api.deezer_controller.requests.get')
def test_get_tracks_info_success(mock_get):
    """Test getting tracks info successfully."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "id": 123456,
        "title": "Test Track",
        "duration": 180,  # Deezer returns seconds
        "rank": 75,
        "album": {"id": 789},
        "artist": {"name": "Test Artist"},
        "preview": "http://example.com/preview.mp3",
        "link": "http://deezer.com/track/123456"
    }
    mock_get.return_value = mock_response
    
    controller = DeezerController("test_id", "test_secret")
    result = controller.get_tracks_info("test_token", ["123456"])
    
    assert len(result["tracks_info"]) == 1
    track = result["tracks_info"][0]
    assert track["deezer_id"] == 123456
    assert track["name"] == "Test Track"
    assert track["duration_ms"] == 180000  # Should be converted to milliseconds
    assert track["popularity"] == 75
    assert track["album_id"] == 789
    assert track["artist_name"] == "Test Artist"


@patch('digster_api.deezer_controller.requests.get')
def test_get_albums_info_success(mock_get):
    """Test getting albums info successfully."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "id": 789,
        "title": "Test Album",
        "artist": {"name": "Test Artist", "id": 456},
        "release_date": "2023-01-01",
        "nb_tracks": 12,
        "cover_medium": "http://example.com/cover.jpg",
        "genres": {"data": [{"name": "Rock"}, {"name": "Pop"}]},
        "label": "Test Label",
        "upc": "123456789012",
        "link": "http://deezer.com/album/789"
    }
    mock_get.return_value = mock_response
    
    controller = DeezerController("test_id", "test_secret")
    result = controller.get_albums_info("test_token", ["789"])
    
    assert len(result["albums_info"]) == 1
    album = result["albums_info"][0]
    assert album["deezer_id"] == 789
    assert album["name"] == "Test Album"
    assert album["artist_name"] == "Test Artist"
    assert album["artist_id"] == 456
    assert album["release_date"] == "2023-01-01"
    assert album["total_tracks"] == 12
    assert album["genres"] == "Rock, Pop"


@patch('digster_api.deezer_controller.requests.get')
def test_get_artists_info_success(mock_get):
    """Test getting artists info successfully."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "id": 456,
        "name": "Test Artist",
        "nb_fan": 50000,
        "picture_medium": "http://example.com/artist.jpg",
        "link": "http://deezer.com/artist/456"
    }
    mock_get.return_value = mock_response
    
    controller = DeezerController("test_id", "test_secret")
    result = controller.get_artists_info("test_token", ["456"])
    
    assert len(result["artists_info"]) == 1
    artist = result["artists_info"][0]
    assert artist["deezer_id"] == 456
    assert artist["name"] == "Test Artist"
    assert artist["nb_fans"] == 50000
    assert artist["image_url"] == "http://example.com/artist.jpg"


@patch('digster_api.deezer_controller.requests.get')
def test_get_user_saved_albums_limit_success(mock_get):
    """Test getting user saved albums with pagination."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "data": [
            {
                "id": 789,
                "title": "Test Album",
                "artist": {"name": "Test Artist", "id": 456},
                "release_date": "2023-01-01",
                "nb_tracks": 12,
                "cover_medium": "http://example.com/cover.jpg",
                "record_type": "album",
                "link": "http://deezer.com/album/789"
            }
        ],
        "total": 1,
        "next": None,
        "prev": None
    }
    mock_get.return_value = mock_response
    
    controller = DeezerController("test_id", "test_secret")
    tokens = {"access_token": "test_token"}
    result = controller.get_user_saved_albums_limit(tokens)
    
    assert len(result["albums"]) == 1
    assert result["total"] == 1
    album = result["albums"][0]
    assert album["deezer_id"] == 789
    assert album["name"] == "Test Album"


def test_get_user_saved_albums_limit_no_token():
    """Test getting saved albums without access token raises error."""
    controller = DeezerController("test_id", "test_secret")
    tokens = {}  # No access token
    
    with pytest.raises(DeezerAuthenticationError):
        controller.get_user_saved_albums_limit(tokens)


@patch('digster_api.deezer_controller.requests.get')
def test_get_tracks_attributes_fallback(mock_get):
    """Test that get_tracks_attributes falls back to get_tracks_info."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "id": 123456,
        "title": "Test Track",
        "duration": 180,
        "rank": 75,
        "album": {"id": 789},
        "artist": {"name": "Test Artist"},
        "preview": "http://example.com/preview.mp3",
        "link": "http://deezer.com/track/123456"
    }
    mock_get.return_value = mock_response
    
    controller = DeezerController("test_id", "test_secret")
    result = controller.get_tracks_attributes("test_token", ["123456"])
    
    # Should return the same structure as get_tracks_info
    assert "tracks_info" in result
    assert len(result["tracks_info"]) == 1


@patch('digster_api.deezer_controller.requests.get')
def test_api_error_handling(mock_get):
    """Test API error handling."""
    mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")
    
    controller = DeezerController("test_id", "test_secret")
    
    with pytest.raises(DeezerAPIError):
        controller.get_user_info("test_token")


@patch('digster_api.deezer_controller.requests.get')
def test_network_error_handling(mock_get):
    """Test network error handling."""
    mock_get.side_effect = requests.exceptions.RequestException("Network error")
    
    controller = DeezerController("test_id", "test_secret")
    
    with pytest.raises(DeezerAPIError):
        controller.get_user_info("test_token")