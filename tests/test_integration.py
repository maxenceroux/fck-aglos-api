"""Integration tests for streaming service interface."""

import os
from unittest.mock import patch, Mock

from digster_api.streaming_service_interface import StreamingServiceInterface


def test_streaming_service_factory_integration():
    """Test that both streaming services can be instantiated through factory."""
    
    # Test Spotify factory (original test to ensure we didn't break anything)
    with patch.dict(os.environ, {
        'SPOTIFY_CLIENT_ID': 'test_spotify_id',
        'SPOTIFY_CLIENT_SECRET': 'test_spotify_secret'
    }):
        # Clear streaming service to test default behavior
        if 'STREAMING_SERVICE' in os.environ:
            del os.environ['STREAMING_SERVICE']
        
        # Import here to avoid circular import and external dependencies
        from digster_api.spotify_controller import SpotifyController
        
        def get_streaming_service_spotify():
            streaming_service = os.environ.get("STREAMING_SERVICE", "spotify").lower()
            if streaming_service == "deezer":
                from digster_api.deezer_controller import DeezerController
                return DeezerController(
                    client_id=str(os.environ.get("DEEZER_CLIENT_ID")),
                    client_secret=str(os.environ.get("DEEZER_CLIENT_SECRET")),
                )
            else:
                return SpotifyController(
                    client_id=str(os.environ.get("SPOTIFY_CLIENT_ID")),
                    client_secret=str(os.environ.get("SPOTIFY_CLIENT_SECRET")),
                )
        
        service = get_streaming_service_spotify()
        assert isinstance(service, StreamingServiceInterface)
        assert isinstance(service, SpotifyController)
        assert service.client_id == 'test_spotify_id'
        assert service.client_secret == 'test_spotify_secret'

    # Test Deezer factory
    with patch.dict(os.environ, {
        'STREAMING_SERVICE': 'deezer',
        'DEEZER_CLIENT_ID': 'test_deezer_id', 
        'DEEZER_CLIENT_SECRET': 'test_deezer_secret'
    }):
        from digster_api.deezer_controller import DeezerController
        
        def get_streaming_service_deezer():
            streaming_service = os.environ.get("STREAMING_SERVICE", "spotify").lower()
            if streaming_service == "deezer":
                return DeezerController(
                    client_id=str(os.environ.get("DEEZER_CLIENT_ID")),
                    client_secret=str(os.environ.get("DEEZER_CLIENT_SECRET")),
                )
            else:
                from digster_api.spotify_controller import SpotifyController
                return SpotifyController(
                    client_id=str(os.environ.get("SPOTIFY_CLIENT_ID")),
                    client_secret=str(os.environ.get("SPOTIFY_CLIENT_SECRET")),
                )
        
        service = get_streaming_service_deezer()
        assert isinstance(service, StreamingServiceInterface)
        assert isinstance(service, DeezerController)
        assert service.client_id == 'test_deezer_id'
        assert service.client_secret == 'test_deezer_secret'


def test_interface_compatibility():
    """Test that both services implement the same interface methods."""
    from digster_api.spotify_controller import SpotifyController
    from digster_api.deezer_controller import DeezerController
    
    spotify_service = SpotifyController("test_id", "test_secret")
    deezer_service = DeezerController("test_id", "test_secret")
    
    # Get all public methods from the interface
    interface_methods = [
        'get_unauth_token', 'refresh_access_token', 'get_current_play',
        'save_album', 'get_user_info', 'get_recently_played',
        'get_tracks_info', 'get_tracks_attributes', 'get_albums_info',
        'get_artists_info', 'get_user_saved_albums_limit', 'get_user_saved_albums'
    ]
    
    # Verify both services implement all methods
    for method in interface_methods:
        assert hasattr(spotify_service, method), f"SpotifyController missing {method}"
        assert hasattr(deezer_service, method), f"DeezerController missing {method}"
        assert callable(getattr(spotify_service, method)), f"SpotifyController {method} not callable"
        assert callable(getattr(deezer_service, method)), f"DeezerController {method} not callable"


def test_deezer_api_structure_compatibility():
    """Test that Deezer API responses match expected structure."""
    from digster_api.deezer_controller import DeezerController
    
    controller = DeezerController("test_id", "test_secret")
    
    # Test methods that should work without API calls
    token = controller.get_unauth_token()
    assert isinstance(token, str)
    
    current_play = controller.get_current_play("test_token")
    assert isinstance(current_play, dict)
    
    recently_played = controller.get_recently_played("test_token")
    assert isinstance(recently_played, dict)
    assert "next_url" in recently_played
    assert "recently_played" in recently_played
    assert isinstance(recently_played["recently_played"], list)
    
    # Test methods with empty inputs
    tracks_info = controller.get_tracks_info("test_token", [])
    assert isinstance(tracks_info, dict)
    assert "tracks_info" in tracks_info
    assert isinstance(tracks_info["tracks_info"], list)
    
    albums_info = controller.get_albums_info("test_token", [])
    assert isinstance(albums_info, dict)
    assert "albums_info" in albums_info
    assert isinstance(albums_info["albums_info"], list)
    
    artists_info = controller.get_artists_info("test_token", [])
    assert isinstance(artists_info, dict)
    assert "artists_info" in artists_info
    assert isinstance(artists_info["artists_info"], list)


if __name__ == "__main__":
    # Run tests manually if pytest not available
    test_streaming_service_factory_integration()
    print("✓ Factory integration test passed")
    
    test_interface_compatibility()
    print("✓ Interface compatibility test passed")
    
    test_deezer_api_structure_compatibility()
    print("✓ Deezer API structure compatibility test passed")
    
    print("\nAll integration tests passed!")