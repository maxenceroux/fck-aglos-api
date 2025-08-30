"""Social/follow-related routes."""

import os
from typing import Any, Dict

from fastapi import APIRouter

from ..database.connection import DigsterDB

router = APIRouter()


@router.post("/description")
def set_description(user_id: str, description: str):
    """Update user description."""
    with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
        db.update_description(user_id, description)
    return description


@router.post("/follow")
def set_user_follows(follower_id: str, following_id: str) -> Dict[str, Any]:
    """Follow or unfollow a user."""
    with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
        query = f"""SELECT * FROM follows
        WHERE follower_id = '{follower_id}'
        and following_id = '{following_id}'"""
        result = db.run_select_query(query)
        if not result:
            follow = {
                "follower_id": follower_id,
                "following_id": following_id,
                "is_following": True,
            }
            db.insert_follow(follow)
            return follow
        if result[0]["is_following"]:
            follow = {
                "follower_id": follower_id,
                "following_id": following_id,
                "is_following": False,
            }
        else:
            follow = {
                "follower_id": follower_id,
                "following_id": following_id,
                "is_following": True,
            }
        db.update_follow(follow)
    return follow


@router.get("/follow")
def get_follow(follower_id: str, following_id: str) -> bool:
    """Check if user is following another user."""
    with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
        query = f"""SELECT * FROM follows
        WHERE follower_id = '{follower_id}'
        and following_id = '{following_id}'"""
        result = db.run_select_query(query)
        if not result:
            return False
    return result[0]["is_following"]


@router.get("/followers")
def get_followers(user_id: str):
    """Get user's followers."""
    with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
        following_id = str(user_id)
        query = f"""
        SELECT users.display_name, users.image_url, users.id,
        case when 
            (select count(*) 
            from follows 
            where following_id = users.id and follower_id = '{following_id}' and is_following is True)
            >0 
            then True else False end as following
        FROM FOLLOWS
        LEFT JOIN USERS ON USERS.ID = FOLLOWS.FOLLOWER_ID
        WHERE FOLLOWING_ID = '{following_id}'
        and is_following is True
        """
        result = db.run_select_query(query)
    return result


@router.get("/following")
def get_following(user_id: str):
    """Get users that the user is following."""
    with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
        follower_id = str(user_id)
        query = f"""
        SELECT users.display_name, users.image_url, users.id
        FROM FOLLOWS
        LEFT JOIN USERS ON USERS.ID = FOLLOWS.FOLLOWING_ID
        WHERE FOLLOWER_ID = '{follower_id}'
        and is_following is True
        """
        result = db.run_select_query(query)
    return result


@router.get("/albums")
def get_albums(
    user_id: str, offset: int = 0, limit: int = 50, sort: str = "random"
):
    """Get user's albums with sorting options."""
    if sort == "random":
        sorting_condition = "ORDER BY random()"
    elif sort == "alphabetical":
        sorting_condition = "ORDER BY albums.name"
    elif sort == "added_to_collection":
        sorting_condition = "ORDER BY added_at DESC"
    elif sort == "release_date":
        sorting_condition = "ORDER BY release_date DESC"
    elif sort == "color":
        sorting_condition = "ORDER BY luminance DESC"

    query = f"""
    SELECT 
        albums.name, 
        albums.label,
        albums.spotify_id,
        albums.image_url,
        artists.name as artist_name,
        user_albums.added_at,
        albums.release_date,
        ('x'||substring(primary_color, 2, 2))::bit(8)::int AS red,
       ('x'||substring(primary_color, 4, 2))::bit(8)::int AS green,
       ('x'||substring(primary_color, 6, 2))::bit(8)::int AS blue,
       (0.299 * ('x'||substring(primary_color, 2, 2))::bit(8)::int +
        0.587 * ('x'||substring(primary_color, 4, 2))::bit(8)::int +
        0.114 * ('x'||substring(primary_color, 6, 2))::bit(8)::int) AS luminance
    FROM
        albums
    LEFT JOIN artists
        ON albums.artist_id = artists.id
    INNER JOIN user_albums 
        ON user_albums.album_id = albums.id
    WHERE user_albums.user_id = '{user_id}'
    {sorting_condition}
    LIMIT {limit} OFFSET {offset}
    
    """
    with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
        result = db.run_select_query(query)
    return result