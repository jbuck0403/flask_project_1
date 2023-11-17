"""empty message

Revision ID: d3921e43a0ec
Revises: 03f74740d815
Create Date: 2023-11-16 20:22:01.262605

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3921e43a0ec'
down_revision = '03f74740d815'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pkmn_moves',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('flavorText', sa.String(), nullable=False),
    sa.Column('power', sa.Integer(), nullable=False),
    sa.Column('damageClass', sa.String(), nullable=False),
    sa.Column('accuracy', sa.Integer(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=False),
    sa.Column('pp', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pkmn_moves')
    # ### end Alembic commands ###
