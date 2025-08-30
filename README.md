# FastAPI for Digster API

## Streaming Services Support

This API supports multiple streaming services through a unified interface:

- **Spotify** - Full OAuth2 implementation with user authorization
- **Deezer** - Public API access with OAuth2 for user features  
- **Apple Music** - JWT-based authentication for catalog access

### Apple Music Integration

The Apple Music client implements the `StreamingServiceInterface` and provides:

#### Setup
Set the following environment variables:
```bash
APPLE_MUSIC_TEAM_ID=your_team_id
APPLE_MUSIC_KEY_ID=your_key_id
```

#### Usage
```python
from digster_api.apple_music_controller import AppleMusicController

# Initialize client
client = AppleMusicController(
    client_id="your_team_id",
    client_secret="your_key_id"
)

# Get developer token
token = client.get_unauth_token()

# Search for tracks, albums, artists
tracks = client.get_tracks_info(token, ["track_id_1", "track_id_2"])
albums = client.get_albums_info(token, ["album_id_1"])
artists = client.get_artists_info(token, ["artist_id_1"])
```

#### Limitations
- User-specific operations (current playback, saved albums) require user authorization
- Audio features are not available through Apple Music API
- JWT tokens are generated locally for catalog access

### Factory Function
Use the factory function to switch between services:
```python
from digster_api.main import get_streaming_service

# Get different services
spotify = get_streaming_service("spotify")
apple_music = get_streaming_service("apple_music") 
deezer = get_streaming_service("deezer")
```

# Activate virtual env
```sh
poetry shell
code .
```
# Run
## Locally
```sh
make start-local
```
## Within containers
```sh
make start-dev-docker
```
# Test
```sh
make test-local
```
## With coverage
```sh
make test-cov-local
```
# Migrate
```sh
make migrate-db
```

# Todo
- Check post to put endpoints
- change sql request to extract tracks using timestamp strategy
- Review typings on `spotify_controller.py`
- Integration tests
- [multiple environments compose files: dev - ci - prod](https://docs.docker.com/compose/extends/#different-environments)
