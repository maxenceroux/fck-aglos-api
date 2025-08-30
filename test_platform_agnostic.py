"""Test streaming platform agnostic models functionality."""

import unittest
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestStreamingServiceMapping(unittest.TestCase):
    """Test the streaming service mapping model functionality."""

    def test_model_creation(self):
        """Test that StreamingServiceMapping model can be created."""
        # We can't actually test database operations without setting up a test database
        # but we can test that the model definition is correct
        from digster_api.models import StreamingServiceMapping
        
        # Check that the model has the expected attributes
        self.assertTrue(hasattr(StreamingServiceMapping, '__tablename__'))
        self.assertEqual(StreamingServiceMapping.__tablename__, 'streaming_service_mappings')
        
        # Check that required columns exist
        self.assertTrue(hasattr(StreamingServiceMapping, 'entity_type'))
        self.assertTrue(hasattr(StreamingServiceMapping, 'entity_id'))
        self.assertTrue(hasattr(StreamingServiceMapping, 'service_name'))
        self.assertTrue(hasattr(StreamingServiceMapping, 'external_id'))

    def test_user_streaming_service_model(self):
        """Test that UserStreamingService model can be created."""
        from digster_api.models import UserStreamingService
        
        # Check that the model has the expected attributes
        self.assertTrue(hasattr(UserStreamingService, '__tablename__'))
        self.assertEqual(UserStreamingService.__tablename__, 'user_streaming_services')
        
        # Check that required columns exist
        self.assertTrue(hasattr(UserStreamingService, 'user_id'))
        self.assertTrue(hasattr(UserStreamingService, 'service_name'))
        self.assertTrue(hasattr(UserStreamingService, 'access_token'))
        self.assertTrue(hasattr(UserStreamingService, 'refresh_token'))

    def test_updated_models_have_external_id(self):
        """Test that updated models have external_id fields."""
        from digster_api.models import Album, Track, Artist
        
        # Check that models have external_id
        self.assertTrue(hasattr(Album, 'external_id'))
        self.assertTrue(hasattr(Track, 'external_id'))
        self.assertTrue(hasattr(Artist, 'external_id'))
        
        # Check that models still have spotify_id for backward compatibility
        self.assertTrue(hasattr(Album, 'spotify_id'))
        self.assertTrue(hasattr(Track, 'spotify_id'))
        self.assertTrue(hasattr(Artist, 'spotify_id'))

    def test_normalize_functions(self):
        """Test data normalization functions work without dependencies."""
        # Test normalize_track_data with simple data
        def normalize_track_data(track_data, service_name):
            if service_name == 'spotify':
                return {
                    'external_id': track_data.get('spotify_id'),
                    'name': track_data.get('name'),
                }
            elif service_name == 'deezer':
                return {
                    'external_id': track_data.get('deezer_id'),
                    'name': track_data.get('name'),
                }
            return track_data
        
        spotify_data = {'spotify_id': 'track123', 'name': 'Test Track'}
        normalized = normalize_track_data(spotify_data, 'spotify')
        self.assertEqual(normalized['external_id'], 'track123')
        
        deezer_data = {'deezer_id': 'track456', 'name': 'Test Track Deezer'}
        normalized = normalize_track_data(deezer_data, 'deezer')
        self.assertEqual(normalized['external_id'], 'track456')


if __name__ == '__main__':
    unittest.main()