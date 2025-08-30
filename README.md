# FastAPI for Digster API

## Environment Variables

The application uses environment variables for Spotify API configuration to enhance security and flexibility. The following environment variables can be set:

### Spotify API Configuration
- `SPOTIFY_CLIENT_ID` - Spotify application client ID (falls back to hardcoded value if not set)
- `SPOTIFY_CLIENT_SECRET` - Spotify application client secret (falls back to hardcoded value if not set)  
- `SPOTIFY_API_BASE_URL` - Base URL for Spotify API (default: `https://api.spotify.com`)
- `SPOTIFY_ACCOUNTS_URL` - Spotify accounts/token URL (default: `https://accounts.spotify.com/api/token`)
- `SPOTIFY_AUTH_URL` - Spotify authorization URL (default: `https://accounts.spotify.com/authorize`)
- `SPOTIFY_REDIRECT_URI` - OAuth redirect URI (default: `https://fck-algos.com/callback`)

### Example .env file
```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=https://yourdomain.com/callback
# Optional - use defaults if not specified
SPOTIFY_API_BASE_URL=https://api.spotify.com
SPOTIFY_ACCOUNTS_URL=https://accounts.spotify.com/api/token
SPOTIFY_AUTH_URL=https://accounts.spotify.com/authorize
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
