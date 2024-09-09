"""empty message

Revision ID: 906976097856
Revises: 47eb6f793b69
Create Date: 2024-09-06 15:46:29.489289

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '906976097856'
down_revision = '47eb6f793b69'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('albums', 'fetched_genres_date')
    op.drop_column('albums', 'fetched_colors_date')
    op.add_column('user_albums', sa.Column('user_spotify_id', sa.Integer(), nullable=True))
    op.add_column('user_albums', sa.Column('album_spotify_id', sa.String(), nullable=True))
    op.drop_index('ix_user_albums_album_id', table_name='user_albums')
    op.drop_index('ix_user_albums_user_id', table_name='user_albums')
    op.create_index(op.f('ix_user_albums_album_spotify_id'), 'user_albums', ['album_spotify_id'], unique=False)
    op.create_index(op.f('ix_user_albums_user_spotify_id'), 'user_albums', ['user_spotify_id'], unique=False)
    op.drop_column('user_albums', 'album_id')
    op.drop_column('user_albums', 'user_id')
    op.drop_column('users', 'spotify_access_token')
    op.drop_column('users', 'spotify_refresh_token')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('spotify_refresh_token', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('spotify_access_token', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('user_albums', sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('user_albums', sa.Column('album_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_user_albums_user_spotify_id'), table_name='user_albums')
    op.drop_index(op.f('ix_user_albums_album_spotify_id'), table_name='user_albums')
    op.create_index('ix_user_albums_user_id', 'user_albums', ['user_id'], unique=False)
    op.create_index('ix_user_albums_album_id', 'user_albums', ['album_id'], unique=False)
    op.drop_column('user_albums', 'album_spotify_id')
    op.drop_column('user_albums', 'user_spotify_id')
    op.add_column('albums', sa.Column('fetched_colors_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('albums', sa.Column('fetched_genres_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
