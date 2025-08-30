"""Authentication routes."""

import os
import requests
from typing import Dict

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

from ..config.settings import settings
from ..database.connection import DigsterDB
from ..services import get_streaming_service

router = APIRouter()


@router.get("/login")
async def login():
    """Initiate Spotify OAuth login."""
    auth_query_parameters = {
        "response_type": "code",
        "client_id": settings.CLIENT_ID,
        "scope": " ".join(settings.SCOPE),
        "redirect_uri": settings.REDIRECT_URI,
    }
    url_args = "&".join(
        [f"{key}={val}" for key, val in auth_query_parameters.items()]
    )
    auth_url = f"{settings.AUTH_URL}/?{url_args}"
    return RedirectResponse(auth_url)


@router.get("/callback")
async def callback(request: Request):
    """Handle OAuth callback from Spotify."""
    code = request.query_params.get("code")

    if code is None:
        raise HTTPException(
            status_code=400, detail="Code not found in the request"
        )

    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.REDIRECT_URI,
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
    }

    r = requests.post(settings.TOKEN_URL, data=token_data)

    if r.status_code != 200:
        raise HTTPException(
            status_code=r.status_code, detail="Failed to fetch tokens"
        )

    token_info = r.json()
    access_token = token_info.get("access_token")
    refresh_token = token_info.get("refresh_token")
    sp_client = get_streaming_service()
    user = sp_client.get_user_info(access_token)
    with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
        db.insert_user(user, access_token, refresh_token)
        if not db.follows(user["id"], "1138415959"):
            db.insert_follow(
                {
                    "follower_id": user["id"],
                    "following_id": "1138415959",
                    "is_following": True,
                }
            )
    return RedirectResponse(f"https://fck-algos.com?user_id={user.get('id')}")


@router.get("/")
def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "API is running"}