"""empty message

Revision ID: 7f07e9d45faf
Revises: 55cfe6679f9d
Create Date: 2023-11-20 00:50:42.023384

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7f07e9d45faf"
down_revision = "55cfe6679f9d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("turn", schema=None) as batch_op:
        batch_op.drop_column("enemyPkmnMove")
        batch_op.drop_column("enemyPkmnShiny")
        batch_op.drop_column("playerPkmnMove")
        batch_op.drop_column("playerPkmnLevel")
        batch_op.drop_column("enemyPkmnLevel")
        batch_op.drop_column("playerPkmnShiny")
        batch_op.drop_column("enemyPkmnPosition")
        batch_op.drop_column("playerPkmnPosition")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("turn", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "playerPkmnPosition", sa.INTEGER(), autoincrement=False, nullable=False
            )
        )
        batch_op.add_column(
            sa.Column(
                "enemyPkmnPosition", sa.INTEGER(), autoincrement=False, nullable=False
            )
        )
        batch_op.add_column(
            sa.Column(
                "playerPkmnShiny", sa.BOOLEAN(), autoincrement=False, nullable=False
            )
        )
        batch_op.add_column(
            sa.Column(
                "enemyPkmnLevel", sa.INTEGER(), autoincrement=False, nullable=False
            )
        )
        batch_op.add_column(
            sa.Column(
                "playerPkmnLevel", sa.INTEGER(), autoincrement=False, nullable=False
            )
        )
        batch_op.add_column(
            sa.Column(
                "playerPkmnMove", sa.INTEGER(), autoincrement=False, nullable=False
            )
        )
        batch_op.add_column(
            sa.Column(
                "enemyPkmnShiny", sa.BOOLEAN(), autoincrement=False, nullable=False
            )
        )
        batch_op.add_column(
            sa.Column(
                "enemyPkmnMove", sa.INTEGER(), autoincrement=False, nullable=False
            )
        )

    # ### end Alembic commands ###