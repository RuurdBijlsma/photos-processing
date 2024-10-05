"""add gps-time column

Revision ID: 8dfae7cf47fc
Revises: d6e8af1c2fb5
Create Date: 2024-10-05 21:50:31.941871

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8dfae7cf47fc'
down_revision: Union[str, None] = 'd6e8af1c2fb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('images', sa.Column('gps_datetime', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('images', 'gps_datetime')
    # ### end Alembic commands ###
