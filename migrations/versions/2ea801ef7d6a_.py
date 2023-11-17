"""empty message

Revision ID: 2ea801ef7d6a
Revises: d3921e43a0ec
Create Date: 2023-11-16 20:33:34.214506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ea801ef7d6a'
down_revision = 'd3921e43a0ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('moves_learned_by_pokemon',
    sa.Column('pkmn_id', sa.Integer(), nullable=True),
    sa.Column('move_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['move_id'], ['pkmn_moves.id'], ),
    sa.ForeignKeyConstraint(['pkmn_id'], ['pkmn.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('moves_learned_by_pokemon')
    # ### end Alembic commands ###
