"""Application configuration management."""

import os
from typing import List, Optional


class Settings:
    """Application settings."""
    
    # Spotify Configuration
    SPOTIFY_CLIENT_ID: str = os.environ.get("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
    
    # Apple Music Configuration
    APPLE_MUSIC_TEAM_ID: str = os.environ.get("APPLE_MUSIC_TEAM_ID", "")
    APPLE_MUSIC_KEY_ID: str = os.environ.get("APPLE_MUSIC_KEY_ID", "")
    
    # Deezer Configuration
    DEEZER_CLIENT_ID: str = os.environ.get("DEEZER_CLIENT_ID", "")
    DEEZER_CLIENT_SECRET: str = os.environ.get("DEEZER_CLIENT_SECRET", "")
    
    # Application Configuration
    REDIRECT_URI: str = os.environ.get("REDIRECT_URI", "https://fck-algos.com/callback")
    AUTH_URL: str = "https://accounts.spotify.com/authorize"
    TOKEN_URL: str = "https://accounts.spotify.com/api/token"
    SCOPE: List[str] = ["user-library-read", "user-library-modify"]
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3003", 
        "https://fck-algos.com",
        "http://192.168.0.10:3005",
    ]
    
    # Database Configuration
    DATABASE_URL: str = os.environ.get("DATABASE_URL_LOCAL", "")
    
    # Default client credentials (should be moved to environment variables)
    CLIENT_ID: str = "b45b68c4c7a0421589605adf1e1a7626"
    CLIENT_SECRET: str = "9f629374960a45aa8268eab3a9dbe18b"


settings = Settings()