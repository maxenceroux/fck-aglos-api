"""Album-related routes."""

import os
from typing import Any, Dict

from fastapi import APIRouter

from ..database.connection import DigsterDB
from ..services import get_streaming_service

router = APIRouter()


@router.put("/album")
def save_album(user_id: str, album_id: str):
    """Save an album to user's library."""
    with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
        user_id = str(user_id)
        user_tokens = db.get_user_spotify_tokens(user_id)
    streaming_client = get_streaming_service()
    try:
        streaming_client.save_album(user_tokens, album_id)
    except Exception as e:
        raise e


@router.get("/random_album")
def get_random_album(
    user_id: str,
    styles: str = None,
    curator: str = None,
    label: str = None,
    year: str = None,
    current_album_id: int = 999999,
):
    """Get a random album based on filters."""
    album_condition = f"""
    WHERE ALBUMS.ID in
            (SELECT ALBUM_ID
                FROM FOLLOWING_USERS_ALBUMS)
    AND ALBUMS.ID <> {current_album_id}
    AND ALBUMS.PRIMARY_COLOR IS NOT NULL
    AND STYLE IS NOT NULL 
    """
    if not user_id:
        user_id = -1
    if label:
        album_condition += f"""
        AND ALBUMS.label = '{label}'
        """
    if year:
        album_condition += f"""
        AND left(ALBUMS.release_date,4) = '{year}'
        """
    if curator:
        curators_list = curator.split(",")
        curators = ", ".join(f"'{curator}'" for curator in curators_list)
        curator_condition = f"""HAVING ARRAY_AGG(DISTINCT ALBUMS_ALL.DISPLAY_NAME 
        ORDER BY ALBUMS_ALL.DISPLAY_NAME)::text[] @> 
        ARRAY[{curators}]::text[]"""
    else:
        curator_condition = ""

    if styles:
        styles_list = styles.split(",")
        styles = ", ".join(f"'{style}'" for style in styles_list)
        styles_count = len(styles_list)
        if curator_condition == "":
            having_condition = f"""HAVING ARRAY_AGG(DISTINCT ALBUMS_ALL.STYLE 
            ORDER BY ALBUMS_ALL.STYLE)::text[] @> 
            ARRAY[{styles}]::text[]"""
        else:
            having_condition = f"""AND ARRAY_AGG(DISTINCT ALBUMS_ALL.STYLE 
            ORDER BY ALBUMS_ALL.STYLE)::text[] @> 
            ARRAY[{styles}]::text[]"""
    else:
        having_condition = ""
    random_album_query = f"""
    WITH FOLLOWING_USERS AS
        (SELECT FOLLOWING_ID
            FROM FOLLOWS
            WHERE FOLLOWER_ID = '{user_id}'
                AND IS_FOLLOWING IS TRUE),
        FOLLOWING_USERS_ALBUMS AS
        (SELECT ALBUM_ID
            FROM USER_ALBUMS
            WHERE USER_ID in
                    (SELECT FOLLOWING_ID
                        FROM FOLLOWING_USERS)
            OR USER_ID = '1138415959'),
        ALBUMS_ALL as (
    SELECT ALBUMS.*,
        ARTISTS.NAME ARTIST_NAME,
        STYLES.STYLE,
        USERS.DISPLAY_NAME

    FROM ALBUMS
    LEFT JOIN ARTISTS ON ARTISTS.ID = ALBUMS.ARTIST_ID
    LEFT JOIN ALBUM_STYLES ON ALBUMS.ID = ALBUM_STYLES.ALBUM_ID
    LEFT JOIN STYLES ON STYLES.ID = ALBUM_STYLES.STYLE_ID
    LEFT JOIN USER_ALBUMS on USER_ALBUMS.ALBUM_ID = ALBUMS.ID
    LEFT JOIN USERS on USER_ALBUMS.USER_ID = USERS.ID
    {album_condition})
    
    SELECT ID,
        SPOTIFY_ID,
        NAME,
        IMAGE_URL,
        LABEL,
        PRIMARY_COLOR,
        SECONDARY_COLOR,
        ARTIST_NAME,
        LEFT(RELEASE_DATE,4) AS RELEASE_DATE_YEAR,
        COUNT(STYLE)
    FROM ALBUMS_ALL
    GROUP BY 1,2,
        3,4,
        5,6,
        7,8,9
        
    {curator_condition}
    {having_condition}
    order by random()
    limit 1
    """
    with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
        if not db.run_select_query(random_album_query):
            return False
        random_album = db.run_select_query(random_album_query)[0]
    return random_album


@router.get("/album_style_genre")
def get_album_style_genre(album_id):
    """Get styles and genres for an album."""
    album_style_query = f"""
    SELECT style 
    FROM album_styles
    left join styles on album_styles.style_id = styles.id
    where album_id = {album_id} 
    """
    album_genre_query = f"""
    SELECT genre 
    FROM album_genres
    left join genres on album_genres.genre_id = genres.id
    where album_id = {album_id} 
    """
    with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
        album_style = db.run_select_query(album_style_query)
        album_genre = db.run_select_query(album_genre_query)
        album_style_genre = {"style": album_style, "genre": album_genre}
    return album_style_genre


@router.get("/album_curators")
def get_album_curators(album_id: str, user_id: str):
    """Get curators for an album."""
    album_curators_query = f"""
    SELECT DISPLAY_NAME,
       IMAGE_URL,
       USERS.ID,
       CASE
           WHEN USERS.ID = '1138415959' THEN TRUE
           ELSE COALESCE(IS_FOLLOWING, FALSE)
       END AS IS_FOLLOWING
FROM USER_ALBUMS
LEFT JOIN USERS ON USERS.ID = USER_ALBUMS.USER_ID
LEFT JOIN FOLLOWS ON FOLLOWER_ID = '{user_id}'
AND FOLLOWING_ID = USERS.ID
WHERE ALBUM_ID = {album_id}
AND (USERS.ID <> '{user_id}' OR '{user_id}' = '1138415959')

    """
    with DigsterDB(db_url=str(os.environ.get("DATABASE_URL"))) as db:
        album_curators = db.run_select_query(album_curators_query)
    return album_curators