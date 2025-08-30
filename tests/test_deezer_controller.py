"""Tests for the Deezer streaming service implementation."""

import pytest
from unittest.mock import Mock, patch

from digster_api.deezer_controller import (
    DeezerController,
    DeezerAuthenticationError,
)
from digster_api.streaming_service_interface import StreamingServiceInterface


def test_deezer_controller_implements_interface():
    """Test that DeezerController correctly implements
    StreamingServiceInterface."""
    # Test instantiation
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
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


def test_deezer_controller_initialization():
    """Test DeezerController initialization."""
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
    )

    assert controller.client_id == "test_id"
    assert controller.client_secret == "test_secret"
    assert controller._base_url == "https://api.deezer.com"


def test_get_unauth_token():
    """Test getting unauthenticated token."""
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
    )

    token = controller.get_unauth_token()
    assert token == "deezer_public_access"


def test_get_current_play():
    """Test getting current play - should return empty dict for Deezer."""
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
    )

    current_play = controller.get_current_play("test_token")
    assert current_play == {}


def test_get_recently_played():
    """Test getting recently played tracks - should return empty list for
    Deezer."""
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
    )

    recently_played = controller.get_recently_played("test_token")
    expected = {"next_url": None, "recently_played": []}
    assert recently_played == expected


def test_get_tracks_attributes():
    """Test getting track attributes - should indicate not supported for
    Deezer."""
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
    )

    attributes = controller.get_tracks_attributes("test_token", ["123"])
    expected = {"message": "Deezer API doesn't support audio features"}
    assert attributes == expected


@patch("digster_api.deezer_controller.requests.get")
def test_get_user_info_success(mock_get):
    """Test successful user info retrieval."""
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
    )

    # Mock successful response
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "id": 12345,
        "name": "Test User",
        "email": "test@example.com",
        "country": "US",
        "picture_medium": "https://example.com/picture.jpg",
    }
    mock_get.return_value = mock_response

    result = controller.get_user_info("test_token")

    expected = {
        "id": "12345",
        "display_name": "Test User",
        "email": "test@example.com",
        "country": "US",
        "image_url": "https://example.com/picture.jpg",
    }
    assert result == expected

    # Verify the request was made correctly
    mock_get.assert_called_once_with(
        "https://api.deezer.com/user/me", params={"access_token": "test_token"}
    )


@patch("digster_api.deezer_controller.requests.get")
def test_get_tracks_info_success(mock_get):
    """Test successful tracks info retrieval."""
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
    )

    # Mock successful response for single track
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "id": 123456,
        "title": "Test Track",
        "duration": 240,  # Deezer returns seconds
        "rank": 75,
        "album": {"id": 789},
    }
    mock_get.return_value = mock_response

    result = controller.get_tracks_info("test_token", ["123456"])

    expected = {
        "tracks_info": [
            {
                "deezer_id": "123456",
                "name": "Test Track",
                "duration_ms": 240000,  # Converted to milliseconds
                "popularity": 75,
                "album_id": "789",
            }
        ]
    }
    assert result == expected


@patch("digster_api.deezer_controller.requests.get")
def test_get_albums_info_success(mock_get):
    """Test successful albums info retrieval."""
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
    )

    # Mock successful response
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "id": 789,
        "title": "Test Album",
        "artist": {"id": 456},
        "genres": {"data": [{"name": "Rock"}, {"name": "Pop"}]},
        "cover_medium": "https://example.com/cover.jpg",
        "label": "Test Label",
        "fans": 1000,
        "release_date": "2023-01-01",
        "nb_tracks": 12,
    }
    mock_get.return_value = mock_response

    result = controller.get_albums_info("test_token", ["789"])

    expected = {
        "albums": [
            {
                "deezer_id": "789",
                "artist_id": "456",
                "genres": "Rock - Pop",
                "image_url": "https://example.com/cover.jpg",
                "label": "Test Label",
                "name": "Test Album",
                "popularity": 1000,
                "release_date": "2023-01-01",
                "total_tracks": 12,
            }
        ]
    }
    assert result == expected


@patch("digster_api.deezer_controller.requests.get")
def test_refresh_access_token_success(mock_get):
    """Test successful access token refresh."""
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
    )

    # Mock successful response
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "access_token=new_token_123&expires=3600"
    mock_get.return_value = mock_response

    result = controller.refresh_access_token("refresh_token_123")

    assert result == "new_token_123"

    # Verify the request was made correctly
    mock_get.assert_called_once_with(
        "https://connect.deezer.com/oauth/access_token.php",
        params={
            "app_id": "test_id",
            "secret": "test_secret",
            "refresh_token": "refresh_token_123",
        },
    )


@patch("digster_api.deezer_controller.requests.get")
def test_refresh_access_token_failure(mock_get):
    """Test failed access token refresh."""
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
    )

    # Mock failed response with HTTPError
    import requests

    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "HTTP Error"
    )
    mock_get.return_value = mock_response

    with pytest.raises(DeezerAuthenticationError):
        controller.refresh_access_token("refresh_token_123")


@patch("digster_api.deezer_controller.requests.post")
def test_save_album_success(mock_post):
    """Test successful album saving."""
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
    )

    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = True
    mock_post.return_value = mock_response

    tokens = {"access_token": "test_token"}
    result = controller.save_album(tokens, "123")

    expected = {"status": "success", "message": "Album saved successfully"}
    assert result == expected


def test_get_tracks_info_empty_ids():
    """Test get_tracks_info with empty track IDs."""
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
    )

    result = controller.get_tracks_info("test_token", [])
    assert result == {"message": "No track IDs provided"}


def test_get_albums_info_empty_ids():
    """Test get_albums_info with empty album IDs."""
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
    )

    result = controller.get_albums_info("test_token", [])
    assert result == {"message": "No album IDs provided"}


def test_get_artists_info_empty_ids():
    """Test get_artists_info with empty artist IDs."""
    controller = DeezerController(
        client_id="test_id", client_secret="test_secret"
    )

    result = controller.get_artists_info("test_token", [])
    assert result == {"message": "No artist IDs provided"}
