"""Streaming service-related routes."""

import os
from typing import Any, Dict

from fastapi import APIRouter

from ..database.connection import DigsterDB
from ..services import get_streaming_service
from ..schemas import AlbumRecRequest
from ..services.email.mailjet_client import MailJetClient

router = APIRouter()


@router.get("/spotify_user_info")
def get_spotify_user_info(token: str) -> Dict[str, Any]:
    """Get Spotify user information."""
    streaming_client = get_streaming_service()
    user = streaming_client.get_user_info(token)
    db = DigsterDB(db_url=str(os.environ.get("DATABASE_URL")))
    db.upsert_user(user)
    db.close_conn()
    return user


@router.post("/album_rec")
def send_album_rec(request: AlbumRecRequest):
    """Send album recommendation email."""
    try:
        with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
            user = db.get_user_info(request.user_id)

        mj_client = MailJetClient(
            os.environ.get("MAILJET_API_KEY"),
            os.environ.get("MAILJET_API_SECRET"),
        )
        variables = {
            "user_url": f"https://open.spotify.com/user{request.user_id}",
            "sp_user_name": user.display_name if user else None,
            "image_url": request.album_image_url,
            "album_name": request.album_name,
            "artist_name": request.artist_name,
            "album_url": request.album_url,
        }
        return mj_client.send_templated_email(
            "hello@fck-algos.com",
            request.recipient_email,
            request.recipient_name,
            6273301,
            "Someone wants to share an album with you!",
            variables,
        )
    except Exception as e:
        print(e)
        raise (e)