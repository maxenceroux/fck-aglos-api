# Streaming Platform Agnostic Implementation

This document describes the changes made to make the Digster API streaming platform agnostic, allowing integration with multiple streaming services like Spotify and Deezer.

## Overview

The original implementation was tightly coupled to Spotify with `spotify_id` fields and `spotify_access_token`/`spotify_refresh_token` in the User model. The new implementation maintains backward compatibility while adding support for multiple streaming services.

## Key Changes

### 1. New Database Models

#### StreamingServiceMapping
Maps internal entity IDs to external streaming service IDs:
- `entity_type`: 'album', 'track', 'artist'
- `entity_id`: Internal database ID
- `service_name`: 'spotify', 'deezer', etc.
- `external_id`: External service ID

#### UserStreamingService
Stores user tokens per streaming service:
- `user_id`: User identifier
- `service_name`: Streaming service name
- `access_token`: Service access token
- `refresh_token`: Service refresh token

### 2. Updated Models

All core models (Album, Track, Artist) now have:
- `external_id`: Generic external ID field
- `spotify_id`: Kept for backward compatibility

### 3. Platform-Agnostic Database Methods

#### Token Management
```python
# Get tokens for any streaming service
db.get_user_streaming_tokens(user_id, 'spotify')
db.get_user_streaming_tokens(user_id, 'deezer')

# Update/insert streaming service tokens
db.upsert_user_streaming_service(user_id, 'spotify', access_token, refresh_token)
```

#### Entity Mapping
```python
# Add mapping between internal and external IDs
db.add_streaming_service_mapping('album', album_id, 'spotify', 'spotify_album_id')
db.add_streaming_service_mapping('album', album_id, 'deezer', 'deezer_album_id')

# Get external ID for a service
external_id = db.get_external_id('album', album_id, 'spotify')

# Find internal ID by external ID
internal_id = db.get_entity_by_external_id('album', 'spotify', 'spotify_album_id')
```

#### Platform-Agnostic Insertion
```python
# Insert artist for any streaming service
artist_id = db.insert_artist_platform_agnostic(
    external_id='artist_123',
    name='Artist Name',
    service_name='spotify'
)

# Insert album for any streaming service
album_id = db.insert_album_platform_agnostic(
    external_id='album_456',
    artist_id=artist_id,
    type='album',
    name='Album Name',
    service_name='deezer'
)
```

### 4. Streaming Service Factory

```python
from digster_api.streaming_service_factory import get_streaming_service

# Get Spotify service
spotify_client = get_streaming_service('spotify')

# Get Deezer service  
deezer_client = get_streaming_service('deezer')

# Use with any service
service_client = get_streaming_service(service_name)
user_info = service_client.get_user_info(token)
```

### 5. Updated API Endpoints

#### Save Album (Platform-Agnostic)
```
PUT /album?user_id={user_id}&album_id={album_id}&service_name={service_name}
```

#### Connect Streaming Service
```
POST /streaming_service/connect
{
    "user_id": "user123",
    "service_name": "deezer", 
    "access_token": "token",
    "refresh_token": "refresh_token"
}
```

#### Get Supported Services
```
GET /streaming_service/supported
Response: {"services": ["spotify", "deezer"]}
```

#### Get User's Connected Services
```
GET /user_streaming_services?user_id={user_id}
Response: {
    "services": [
        {"service_name": "spotify", "created_at": "...", "updated_at": "..."},
        {"service_name": "deezer", "created_at": "...", "updated_at": "..."}
    ]
}
```

## Migration Strategy

### Backward Compatibility
- All `spotify_id` fields are preserved
- Existing Spotify tokens in User model still work
- New `external_id` fields supplement existing fields
- Legacy methods continue to work

### Database Migration
Run the migration script to add new tables and columns:
```bash
alembic upgrade head
```

### Data Migration
To migrate existing Spotify data to the new structure:
1. Copy `spotify_id` values to `external_id` fields
2. Create mappings in `StreamingServiceMapping` table
3. Migrate user tokens to `UserStreamingService` table

## Benefits

1. **Multi-Platform Support**: Easy integration with Spotify, Deezer, and future services
2. **Backward Compatibility**: Existing Spotify functionality continues to work
3. **Scalable**: Simple to add new streaming services
4. **Clean Architecture**: Separation of concerns with factory pattern
5. **Data Normalization**: Unified data structures across services

## Future Enhancements

1. Add more streaming services (Apple Music, YouTube Music, etc.)
2. Implement cross-platform playlist synchronization  
3. Add service-specific features and capabilities
4. Enhanced user preference management per service
5. Analytics and insights across multiple platforms

## Example Usage

```python
# Connect user to multiple services
db.upsert_user_streaming_service(user_id, 'spotify', spotify_access, spotify_refresh)
db.upsert_user_streaming_service(user_id, 'deezer', deezer_access, deezer_refresh)

# Save same album across services
spotify_client = get_streaming_service('spotify')
deezer_client = get_streaming_service('deezer')

spotify_tokens = db.get_user_streaming_tokens(user_id, 'spotify')
deezer_tokens = db.get_user_streaming_tokens(user_id, 'deezer')

spotify_client.save_album(spotify_tokens, spotify_album_id)
deezer_client.save_album(deezer_tokens, deezer_album_id)
```