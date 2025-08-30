"""API routes."""

from .auth import router as auth_router
from .users import router as users_router
from .albums import router as albums_router
from .social import router as social_router
from .streaming import router as streaming_router

__all__ = [
    "auth_router",
    "users_router", 
    "albums_router",
    "social_router",
    "streaming_router",
]