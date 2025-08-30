"""Request and response schemas."""

from pydantic import BaseModel, HttpUrl


class AlbumRecRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    user_id: str
    album_image_url: HttpUrl
    album_name: str
    artist_name: str
    album_url: HttpUrl