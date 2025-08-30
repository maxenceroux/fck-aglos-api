"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config.settings import settings
from .routes import (
    auth_router,
    users_router,
    albums_router,
    social_router,
    streaming_router,
)

# In-memory storage for tokens; use a database for persistent storage
user_tokens = {}

app = FastAPI(title="Digster API", description="A modular music discovery API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, tags=["authentication"])
app.include_router(users_router, tags=["users"])
app.include_router(albums_router, tags=["albums"])
app.include_router(social_router, tags=["social"])
app.include_router(streaming_router, tags=["streaming"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)