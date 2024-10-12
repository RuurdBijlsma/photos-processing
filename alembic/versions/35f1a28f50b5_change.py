"""change

Revision ID: 35f1a28f50b5
Revises: ee6362ba6be6
Create Date: 2024-10-12 22:20:28.297782

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35f1a28f50b5'
down_revision: Union[str, None] = 'ee6362ba6be6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('process_timings',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('time_ns', sa.Integer(), nullable=False),
    sa.Column('iterations', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('process_timings')
    # ### end Alembic commands ###
