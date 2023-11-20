"""empty message

Revision ID: 5539a4e570c1
Revises: 
Create Date: 2023-11-19 19:08:03.250812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5539a4e570c1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "pkmn",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("sprite", sa.String(), nullable=False),
        sa.Column("spriteShiny", sa.String(), nullable=True),
        sa.Column("firstType", sa.String(), nullable=False),
        sa.Column("secondType", sa.String(), nullable=True),
        sa.Column("firstAbility", sa.String(), nullable=False),
        sa.Column("secondAbility", sa.String(), nullable=True),
        sa.Column("hiddenAbility", sa.String(), nullable=True),
        sa.Column("baseEXP", sa.Integer(), nullable=True),
        sa.Column("baseHP", sa.Integer(), nullable=False),
        sa.Column("baseAtk", sa.Integer(), nullable=False),
        sa.Column("baseDef", sa.Integer(), nullable=False),
        sa.Column("baseSpAtk", sa.Integer(), nullable=False),
        sa.Column("baseSpDef", sa.Integer(), nullable=False),
        sa.Column("baseSpd", sa.Integer(), nullable=False),
        sa.Column("spriteBack", sa.String(), nullable=False),
        sa.Column("spriteShinyBack", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pkmn_moves",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("power", sa.String(), nullable=True),
        sa.Column("minHits", sa.String(), nullable=True),
        sa.Column("maxHits", sa.String(), nullable=True),
        sa.Column("ailment", sa.String(), nullable=True),
        sa.Column("ailmentChance", sa.String(), nullable=True),
        sa.Column("moveType", sa.String(), nullable=True),
        sa.Column("critRate", sa.String(), nullable=True),
        sa.Column("drain", sa.String(), nullable=True),
        sa.Column("flinchChance", sa.String(), nullable=True),
        sa.Column("healing", sa.String(), nullable=True),
        sa.Column("maxTurns", sa.String(), nullable=True),
        sa.Column("minTurns", sa.String(), nullable=True),
        sa.Column("statChance", sa.String(), nullable=True),
        sa.Column("damageClass", sa.String(), nullable=True),
        sa.Column("accuracy", sa.String(), nullable=True),
        sa.Column("effectChance", sa.String(), nullable=True),
        sa.Column("priority", sa.String(), nullable=True),
        sa.Column("pp", sa.String(), nullable=True),
        sa.Column("target", sa.String(), nullable=True),
        sa.Column("effect", sa.String(), nullable=True),
        sa.Column("flavorText", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "unown_letters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("sprite", sa.String(), nullable=False),
        sa.Column("spriteShiny", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("userName", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.Column("favoritePkmn", sa.String(length=10), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userName"),
    )
    op.create_table(
        "battle",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("playerID", sa.Integer(), nullable=False),
        sa.Column("enemyID", sa.Integer(), nullable=False),
        sa.Column("dateTime", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["enemyID"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["playerID"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "damage_moves_learned_by_pokemon",
        sa.Column("pkmn_id", sa.Integer(), nullable=True),
        sa.Column("move_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["move_id"],
            ["pkmn_moves.id"],
        ),
        sa.ForeignKeyConstraint(
            ["pkmn_id"],
            ["pkmn.id"],
        ),
    )
    op.create_table(
        "pkmn_team",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pkmnID", sa.Integer(), nullable=False),
        sa.Column("trainerID", sa.Integer(), nullable=False),
        sa.Column("shiny", sa.Boolean(), nullable=False),
        sa.Column("chosenMove", sa.Integer(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["chosenMove"],
            ["pkmn_moves.id"],
        ),
        sa.ForeignKeyConstraint(
            ["pkmnID"],
            ["pkmn.id"],
        ),
        sa.ForeignKeyConstraint(
            ["trainerID"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "status_moves_learned_by_pokemon",
        sa.Column("pkmn_id", sa.Integer(), nullable=True),
        sa.Column("move_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["move_id"],
            ["pkmn_moves.id"],
        ),
        sa.ForeignKeyConstraint(
            ["pkmn_id"],
            ["pkmn.id"],
        ),
    )
    op.create_table(
        "turn",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("battleID", sa.Integer(), nullable=False),
        sa.Column("playerPkmnID", sa.Integer(), nullable=False),
        sa.Column("playerPkmnShiny", sa.Boolean(), nullable=False),
        sa.Column("playerPkmnHP", sa.Integer(), nullable=False),
        sa.Column("playerPkmnDamageTaken", sa.Integer(), nullable=False),
        sa.Column("playerPkmnMove", sa.Integer(), nullable=False),
        sa.Column("playerPkmnLevel", sa.Integer(), nullable=False),
        sa.Column("playerPkmnPosition", sa.Integer(), nullable=False),
        sa.Column("enemyPkmnID", sa.Integer(), nullable=False),
        sa.Column("enemyPkmnShiny", sa.Boolean(), nullable=False),
        sa.Column("enemyPkmnHP", sa.Integer(), nullable=False),
        sa.Column("enemyPkmnDamageTaken", sa.Integer(), nullable=False),
        sa.Column("enemyPkmnMove", sa.Integer(), nullable=False),
        sa.Column("enemyPkmnLevel", sa.Integer(), nullable=False),
        sa.Column("enemyPkmnPosition", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["battleID"],
            ["battle.id"],
        ),
        sa.ForeignKeyConstraint(
            ["enemyPkmnID"],
            ["pkmn.id"],
        ),
        sa.ForeignKeyConstraint(
            ["playerPkmnID"],
            ["pkmn.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "turn_description",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("battleID", sa.Integer(), nullable=False),
        sa.Column("turnID", sa.Integer(), nullable=False),
        sa.Column("eventDescription", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["battleID"],
            ["battle.id"],
        ),
        sa.ForeignKeyConstraint(
            ["turnID"],
            ["turn.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("turn_description")
    op.drop_table("turn")
    op.drop_table("status_moves_learned_by_pokemon")
    op.drop_table("pkmn_team")
    op.drop_table("damage_moves_learned_by_pokemon")
    op.drop_table("battle")
    op.drop_table("user")
    op.drop_table("unown_letters")
    op.drop_table("pkmn_moves")
    op.drop_table("pkmn")
    # ### end Alembic commands ###
