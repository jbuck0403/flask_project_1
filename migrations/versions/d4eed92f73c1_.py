"""empty message

Revision ID: d4eed92f73c1
Revises: 5390b4f3df09
Create Date: 2023-11-17 16:46:34.611346

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4eed92f73c1'
down_revision = '5390b4f3df09'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pkmn_moves', schema=None) as batch_op:
        batch_op.add_column(sa.Column('moveType', sa.String(), nullable=False))
        batch_op.drop_column('type')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pkmn_moves', schema=None) as batch_op:
        batch_op.add_column(sa.Column('type', sa.VARCHAR(), autoincrement=False, nullable=False))
        batch_op.drop_column('moveType')

    # ### end Alembic commands ###
