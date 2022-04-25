"""add_colors

Revision ID: 7db569652867
Revises: bcc4eef0cfe8
Create Date: 2022-04-08 12:56:12.240385

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7db569652867'
down_revision = 'bcc4eef0cfe8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('albums', sa.Column('tertiary_color', sa.String(), nullable=True))
    op.add_column('albums', sa.Column('fourth_color', sa.String(), nullable=True))
    op.add_column('albums', sa.Column('fifth_color', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('albums', 'fifth_color')
    op.drop_column('albums', 'fourth_color')
    op.drop_column('albums', 'tertiary_color')
    # ### end Alembic commands ###
