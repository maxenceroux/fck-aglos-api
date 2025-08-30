"""Add streaming platform agnostic support

Revision ID: streaming_platform_agnostic
Revises: a3cf474a2448
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'streaming_platform_agnostic'
down_revision = 'a3cf474a2448'
branch_labels = None
depends_on = None


def upgrade():
    # Create streaming_service_mappings table
    op.create_table('streaming_service_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('service_name', sa.String(), nullable=True),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_streaming_service_mappings_entity_id'), 'streaming_service_mappings', ['entity_id'], unique=False)
    op.create_index(op.f('ix_streaming_service_mappings_entity_type'), 'streaming_service_mappings', ['entity_type'], unique=False)
    op.create_index(op.f('ix_streaming_service_mappings_external_id'), 'streaming_service_mappings', ['external_id'], unique=False)
    op.create_index(op.f('ix_streaming_service_mappings_id'), 'streaming_service_mappings', ['id'], unique=False)
    op.create_index(op.f('ix_streaming_service_mappings_service_name'), 'streaming_service_mappings', ['service_name'], unique=False)

    # Create user_streaming_services table
    op.create_table('user_streaming_services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('service_name', sa.String(), nullable=True),
        sa.Column('access_token', sa.String(), nullable=True),
        sa.Column('refresh_token', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_streaming_services_id'), 'user_streaming_services', ['id'], unique=False)
    op.create_index(op.f('ix_user_streaming_services_service_name'), 'user_streaming_services', ['service_name'], unique=False)
    op.create_index(op.f('ix_user_streaming_services_user_id'), 'user_streaming_services', ['user_id'], unique=False)

    # Add external_id columns to existing tables (keeping spotify_id for backward compatibility)
    op.add_column('albums', sa.Column('external_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_albums_external_id'), 'albums', ['external_id'], unique=False)
    
    op.add_column('tracks', sa.Column('external_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_tracks_external_id'), 'tracks', ['external_id'], unique=False)
    
    op.add_column('artists', sa.Column('external_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_artists_external_id'), 'artists', ['external_id'], unique=False)


def downgrade():
    # Remove external_id columns and indices
    op.drop_index(op.f('ix_artists_external_id'), table_name='artists')
    op.drop_column('artists', 'external_id')
    
    op.drop_index(op.f('ix_tracks_external_id'), table_name='tracks')
    op.drop_column('tracks', 'external_id')
    
    op.drop_index(op.f('ix_albums_external_id'), table_name='albums')
    op.drop_column('albums', 'external_id')

    # Drop user_streaming_services table
    op.drop_index(op.f('ix_user_streaming_services_user_id'), table_name='user_streaming_services')
    op.drop_index(op.f('ix_user_streaming_services_service_name'), table_name='user_streaming_services')
    op.drop_index(op.f('ix_user_streaming_services_id'), table_name='user_streaming_services')
    op.drop_table('user_streaming_services')

    # Drop streaming_service_mappings table
    op.drop_index(op.f('ix_streaming_service_mappings_service_name'), table_name='streaming_service_mappings')
    op.drop_index(op.f('ix_streaming_service_mappings_id'), table_name='streaming_service_mappings')
    op.drop_index(op.f('ix_streaming_service_mappings_external_id'), table_name='streaming_service_mappings')
    op.drop_index(op.f('ix_streaming_service_mappings_entity_type'), table_name='streaming_service_mappings')
    op.drop_index(op.f('ix_streaming_service_mappings_entity_id'), table_name='streaming_service_mappings')
    op.drop_table('streaming_service_mappings')