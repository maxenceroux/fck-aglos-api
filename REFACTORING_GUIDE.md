# Digster API - Refactored Project Structure

This document describes the new modular structure of the Digster API after refactoring for improved maintainability and scalability.

## Project Structure Overview

```
digster_api/
├── main.py                     # 🎯 Main FastAPI application (33 lines, was 582)
├── config/                     # ⚙️ Configuration management
│   ├── __init__.py
│   └── settings.py            # Centralized settings with environment variables
├── models/                     # 🗄️ Database models (split by entity)
│   ├── __init__.py            # Exports all models
│   ├── base.py                # SQLAlchemy base class
│   ├── user.py                # User, Follow models
│   ├── album.py               # Album, UserAlbum, AlbumGenre, AlbumStyle
│   ├── artist.py              # Artist model
│   ├── track.py               # Track, Listen models
│   └── genre.py               # Genre, Style models
├── schemas/                    # 📋 Pydantic schemas (split by functionality)
│   ├── __init__.py
│   ├── requests.py            # Request schemas (AlbumRecRequest)
│   └── track.py               # Track-related schemas (Listen, Listens)
├── services/                   # 🔧 External service integrations
│   ├── __init__.py            # Service factory exports
│   ├── factory.py             # Streaming service factory function
│   ├── streaming/             # Music streaming services
│   │   ├── __init__.py
│   │   ├── interface.py       # StreamingServiceInterface
│   │   ├── spotify_client.py  # SpotifyController
│   │   ├── deezer_client.py   # DeezerController
│   │   └── apple_music_client.py # AppleMusicController
│   ├── email/                 # Email services
│   │   ├── __init__.py
│   │   └── mailjet_client.py  # MailJetClient
│   └── external/              # Other external APIs
│       ├── __init__.py
│       ├── chartmetric_controller.py
│       └── discogs_controller.py
├── routes/                     # 🛣️ API endpoints (split by functionality)
│   ├── __init__.py            # Router exports
│   ├── auth.py                # Authentication (login, callback)
│   ├── users.py               # User management
│   ├── albums.py              # Album operations
│   ├── social.py              # Social features (follow, etc.)
│   └── streaming.py           # Streaming service endpoints
├── database/                   # 💾 Database connection management
│   ├── __init__.py
│   └── connection.py          # DigsterDB class
├── utils/                      # 🛠️ Utility functions
│   ├── __init__.py
│   └── color_finder.py        # Dominant color extraction
├── workers/                    # ⚡ Background tasks
│   ├── __init__.py
│   ├── tasks.py               # Background task functions
│   └── celery_app.py          # Celery configuration
└── alembic/                    # 📦 Database migrations (preserved)
    └── versions/
```

## Key Changes Made

### 1. **Modular Main Application** (`main.py`)
- **Before**: 582 lines with all routes and logic mixed together
- **After**: 33 lines, clean separation with router includes

```python
# New main.py structure
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config.settings import settings
from .routes import (auth_router, users_router, albums_router, social_router, streaming_router)

app = FastAPI(title="Digster API", description="A modular music discovery API")
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, ...)
app.include_router(auth_router, tags=["authentication"])
app.include_router(users_router, tags=["users"])
# ... other routers
```

### 2. **Configuration Management** (`config/`)
- Centralized settings in `config/settings.py`
- Environment variable management
- No more hardcoded values scattered throughout the codebase

```python
# config/settings.py
class Settings:
    SPOTIFY_CLIENT_ID: str = os.environ.get("SPOTIFY_CLIENT_ID", "")
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://fck-algos.com"]
    # ... other settings
```

### 3. **Split Database Models** (`models/`)
- **Before**: Single `models.py` file with all models mixed together
- **After**: Separate files by entity (user.py, album.py, artist.py, etc.)

```python
# models/user.py
from .base import Base
class User(Base): ...
class Follow(Base): ...

# models/album.py  
from .base import Base
class Album(Base): ...
class UserAlbum(Base): ...
```

### 4. **Organized Services** (`services/`)
- Streaming services grouped under `services/streaming/`
- External APIs in `services/external/`
- Email services in `services/email/`
- Factory function for service instantiation

```python
# services/factory.py
def get_streaming_service(service_type: str = "spotify") -> StreamingServiceInterface:
    if service_type.lower() == "spotify":
        return SpotifyController(...)
    elif service_type.lower() == "deezer":
        return DeezerController(...)
    # ...
```

### 5. **Route Separation** (`routes/`)
- **Before**: All routes in main.py
- **After**: Routes split by functionality

- `auth.py`: Authentication endpoints (login, callback)
- `users.py`: User management (user info, preferences)  
- `albums.py`: Album operations (save, random album, metadata)
- `social.py`: Social features (follow, followers, user albums)
- `streaming.py`: Streaming service specific endpoints

### 6. **Clear Import Patterns**
All modules use relative imports and proper `__init__.py` files for clean exports:

```python
# From routes/users.py
from ..database import DigsterDB
from ..workers import fetch_albums_data
from ..config import settings
```

## Benefits of the New Structure

### 🎯 **Modularity**
- Each module has a single, clear responsibility
- Easy to locate and modify specific functionality
- Reduced coupling between components

### 📈 **Scalability** 
- Easy to add new streaming services in `services/streaming/`
- Simple to add new route categories in `routes/`
- Straightforward to extend models without affecting others

### 🔧 **Maintainability**
- Logical code organization with clear naming conventions
- Predictable import paths
- Smaller, focused files instead of large monolithic ones

### 🧪 **Testability**
- Each module can be tested independently
- Mock dependencies easily with clear interfaces
- Focused unit tests for specific functionality

### ⚙️ **Configuration Management**
- All settings centralized in one place
- Environment-based configuration
- No more searching for hardcoded values

## How to Use the New Structure

### Adding a New Streaming Service
1. Create new client in `services/streaming/new_service_client.py`
2. Implement `StreamingServiceInterface`
3. Add to factory in `services/factory.py`
4. Export in `services/streaming/__init__.py`

### Adding New API Endpoints
1. Create new router file in `routes/new_feature.py`
2. Define router with `router = APIRouter()`
3. Add endpoints with `@router.get("/endpoint")`
4. Include router in `main.py`

### Adding New Database Models
1. Create model file in `models/new_entity.py`
2. Import Base from `models/base.py`
3. Define model class inheriting from Base
4. Export in `models/__init__.py`

### Adding Background Tasks
1. Add task function to `workers/tasks.py`
2. Import and use in routes as needed
3. Configure Celery settings in `workers/celery_app.py`

## Migration Guide

The refactored code maintains the same external API, so existing clients should continue to work without changes. The main differences are:

1. **Import paths have changed** - Internal imports now use the new structure
2. **Configuration is centralized** - Environment variables are managed in `config/settings.py`
3. **Service instantiation** - Use the factory function from `services/`

## Running the Application

The application can still be run the same way:

```bash
# Local development
make start-local

# With Docker
make start-dev-docker

# Tests
make test-local
```

The new structure makes the codebase much more maintainable and follows Python best practices for package organization.