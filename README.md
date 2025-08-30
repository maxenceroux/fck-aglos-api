# FastAPI for Digster API

## Streaming Services

This API supports multiple streaming services through a unified interface:

### Spotify (Default)
- Set environment variables: `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`
- Supports all features including currently playing, recently played, and audio features

### Deezer
- Set environment variables: `DEEZER_CLIENT_ID`, `DEEZER_CLIENT_SECRET`, `STREAMING_SERVICE=deezer`
- Supports basic functionality (some features limited by Deezer API)

To switch between services, set the `STREAMING_SERVICE` environment variable:
```sh
export STREAMING_SERVICE=deezer  # or "spotify" (default)
```

### Deezer API Limitations
- No "currently playing" endpoint available
- No "recently played" endpoint available  
- No audio features/attributes like Spotify
- Refresh tokens not supported (re-authentication required)

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
