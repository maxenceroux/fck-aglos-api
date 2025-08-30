"""User-related routes."""

import os
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks

from ..database.connection import DigsterDB
from ..workers import fetch_albums_data

router = APIRouter()


@router.post("/allow_fetching")
def set_allow_fetching(user_id: str) -> Dict[str, Any]:
    """Toggle user's album fetching allowance."""
    with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
        query = (
            f"SELECT has_allowed_fetching FROM USERS WHERE id = '{user_id}'"
        )
        actual_fetching = db.run_select_query(query)[0]["has_allowed_fetching"]
        if actual_fetching:
            new_fetching = False
        else:
            new_fetching = True
        db.update_fetching_allowance(user_id, new_fetching)
    return new_fetching


@router.get("/user_info")
def get_spotify_user_info(user_id: str) -> Dict[str, Any]:
    """Get user information with stats."""
    query = f"""
    SELECT USERS.DISPLAY_NAME,
	USERS.IMAGE_URL,
	USERS.ID,
    USERS.HAS_ALLOWED_FETCHING,
	COALESCE(FOLLOWING.COUNT,
		0) AS FOLLOWING_COUNT,
	COALESCE(FOLLOWER.COUNT,
		0) AS FOLLOWER_COUNT,
	COALESCE(ALBUMS_COUNT.COUNT,
		0) AS ALBUMS_COUNT
FROM USERS
LEFT JOIN
	(SELECT FOLLOWER_ID,
			COUNT(*)
		FROM FOLLOWS
		WHERE FOLLOWER_ID = '{user_id}'
        AND IS_FOLLOWING IS TRUE
		GROUP BY FOLLOWER_ID) AS FOLLOWING ON FOLLOWER_ID = ID
LEFT JOIN
	(SELECT FOLLOWING_ID,
			COUNT(*)
		FROM FOLLOWS
		WHERE FOLLOWING_ID = '{user_id}'
        AND IS_FOLLOWING IS TRUE
		GROUP BY FOLLOWING_ID) AS FOLLOWER ON FOLLOWING_ID = ID
LEFT JOIN
	(SELECT USER_ID,
			COUNT(*)
		FROM USER_ALBUMS
		WHERE USER_ID = '{user_id}'
        GROUP BY USER_ID) AS ALBUMS_COUNT ON USER_ID = ID
WHERE ID = '{user_id}'
    """
    with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
        user = db.run_select_query(query)[0]
    return user


@router.get("/saved_albums")
def get_saved_albums(
    user_id: str,
    background_task: BackgroundTasks,
):
    """Trigger background task to fetch user's saved albums."""
    background_task.add_task(fetch_albums_data, user_id)
    return {"details": "albums are fetching", "user_id": user_id}


@router.get("/users")
def get_users():
    """Get all users with their stats."""
    query = """
    SELECT USERS.ID,
	USERS.DISPLAY_NAME,
	USERS.IMAGE_URL,
	COALESCE(FOLLOWING.COUNT,
		0) AS FOLLOWING_COUNT,
	COALESCE(FOLLOWER.COUNT,
		0) AS FOLLOWER_COUNT,
	COALESCE(ALBUMS_COUNT.COUNT,
		0) AS ALBUMS_COUNT
FROM USERS
LEFT JOIN
	(SELECT FOLLOWER_ID,
			COUNT(*)
		FROM FOLLOWS
		WHERE IS_FOLLOWING IS TRUE
		GROUP BY FOLLOWER_ID) AS FOLLOWING ON FOLLOWER_ID = ID
LEFT JOIN
	(SELECT FOLLOWING_ID,
			COUNT(*)
		FROM FOLLOWS
		WHERE IS_FOLLOWING IS TRUE
		GROUP BY FOLLOWING_ID) AS FOLLOWER ON FOLLOWING_ID = ID
LEFT JOIN
	(SELECT USER_ID,
			COUNT(*)
		FROM USER_ALBUMS
		GROUP BY USER_ID) AS ALBUMS_COUNT ON USER_ID = ID
ORDER BY FOLLOWER_COUNT DESC,
	ALBUMS_COUNT DESC"""
    with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
        users = db.run_select_query(query)
    return users