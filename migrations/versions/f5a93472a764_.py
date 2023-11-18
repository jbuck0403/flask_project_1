"""empty message

Revision ID: f5a93472a764
Revises: 7ef88be2ea0b
Create Date: 2023-11-17 18:17:32.909401

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5a93472a764'
down_revision = '7ef88be2ea0b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pkmn_moves', schema=None) as batch_op:
        batch_op.alter_column('power',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('minHits',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('maxHits',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('ailmentChance',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('critRate',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('drain',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('flinchChance',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('healing',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('maxTurns',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('minTurns',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('statChance',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('accuracy',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('effectChance',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('priority',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('pp',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pkmn_moves', schema=None) as batch_op:
        batch_op.alter_column('pp',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('priority',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('effectChance',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('accuracy',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('statChance',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('minTurns',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('maxTurns',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('healing',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('flinchChance',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('drain',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('critRate',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('ailmentChance',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('maxHits',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('minHits',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('power',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)

    # ### end Alembic commands ###
