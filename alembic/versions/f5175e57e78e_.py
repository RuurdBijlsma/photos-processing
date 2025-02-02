"""empty message

Revision ID: f5175e57e78e
Revises: a76fc3f9b482
Create Date: 2025-02-02 22:44:02.976963

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvecto_rs.sqlalchemy import VECTOR
from pgvecto_rs.types import IndexOption, Hnsw
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f5175e57e78e'
down_revision: Union[str, None] = 'a76fc3f9b482'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('images', sa.Column('mpf', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('images', sa.Column('use_panorama_viewer', sa.Boolean(), nullable=False))
    op.add_column('images', sa.Column('is_photosphere', sa.Boolean(), nullable=False))
    op.add_column('images', sa.Column('projection_type', sa.Boolean(), nullable=True))
    op.add_column('images', sa.Column('motion_photo_presentation_timestamp', sa.Integer(), nullable=True))
    op.add_column('images', sa.Column('burst_id', sa.String(), nullable=True))
    op.add_column('images', sa.Column('is_video', sa.Boolean(), nullable=False))
    op.add_column('images', sa.Column('capture_fps', sa.Float(), nullable=True))
    op.add_column('images', sa.Column('video_fps', sa.Float(), nullable=True))
    op.drop_column('images', 'is_panorama')
    op.drop_column('images', 'is_360')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('images', sa.Column('is_360', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('images', sa.Column('is_panorama', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('images', 'video_fps')
    op.drop_column('images', 'capture_fps')
    op.drop_column('images', 'is_video')
    op.drop_column('images', 'burst_id')
    op.drop_column('images', 'motion_photo_presentation_timestamp')
    op.drop_column('images', 'projection_type')
    op.drop_column('images', 'is_photosphere')
    op.drop_column('images', 'use_panorama_viewer')
    op.drop_column('images', 'mpf')
    # ### end Alembic commands ###
