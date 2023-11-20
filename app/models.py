from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    dateCreated = db.Column(db.Date, nullable=False, default=datetime.utcnow())
    favoritePkmn = db.Column(db.String(10))

    def __init__(self, userName, password):
        self.userName = userName
        self.password = generate_password_hash(password)


damageMovesLearnableByPokemon = db.Table(
    "damage_moves_learned_by_pokemon",
    db.Column("pkmn_id", db.Integer, db.ForeignKey("pkmn.id")),
    db.Column("move_id", db.Integer, db.ForeignKey("pkmn_moves.id")),
)

statusMovesLearnableByPokemon = db.Table(
    "status_moves_learned_by_pokemon",
    db.Column("pkmn_id", db.Integer, db.ForeignKey("pkmn.id")),
    db.Column("move_id", db.Integer, db.ForeignKey("pkmn_moves.id")),
)


class Pkmn(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    sprite = db.Column(db.String, nullable=False)
    spriteShiny = db.Column(db.String, nullable=True)
    firstType = db.Column(db.String, nullable=False)
    secondType = db.Column(db.String, nullable=True)
    firstAbility = db.Column(db.String, nullable=False)
    secondAbility = db.Column(db.String, nullable=True)
    hiddenAbility = db.Column(db.String, nullable=True)
    baseEXP = db.Column(db.Integer, nullable=True)
    baseHP = db.Column(db.Integer, nullable=False)
    baseAtk = db.Column(db.Integer, nullable=False)
    baseDef = db.Column(db.Integer, nullable=False)
    baseSpAtk = db.Column(db.Integer, nullable=False)
    baseSpDef = db.Column(db.Integer, nullable=False)
    baseSpd = db.Column(db.Integer, nullable=False)
    spriteBack = db.Column(db.String, nullable=False)
    spriteShinyBack = db.Column(db.String, nullable=True)

    # Relationship for damage moves
    damageMoves = relationship(
        "PkmnMoves",
        secondary=damageMovesLearnableByPokemon,
        back_populates="damageMovesLearnedBy",
    )

    # Relationship for status moves
    statusMoves = relationship(
        "PkmnMoves",
        secondary=statusMovesLearnableByPokemon,
        back_populates="statusMovesLearnedBy",
    )

    def __init__(
        self,
        id,
        name,
        sprite,
        spriteShiny,
        spriteBack,
        spriteShinyBack,
        firstType,
        secondType,
        firstAbility,
        secondAbility,
        hiddenAbility,
        baseEXP,
        baseHP,
        baseAtk,
        baseDef,
        baseSpAtk,
        baseSpDef,
        baseSpd,
        form=False,
    ):
        self.id = id
        self.name = name
        self.sprite = sprite
        self.spriteShiny = spriteShiny
        self.spriteBack = spriteBack
        self.spriteShinyBack = spriteShinyBack
        self.firstType = firstType
        self.secondType = secondType
        self.firstAbility = firstAbility
        self.secondAbility = secondAbility
        self.hiddenAbility = hiddenAbility
        self.baseEXP = baseEXP
        self.baseHP = baseHP
        self.baseAtk = baseAtk
        self.baseDef = baseDef
        self.baseSpAtk = baseSpAtk
        self.baseSpDef = baseSpDef
        self.baseSpd = baseSpd


class PkmnMoves(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=True)
    power = db.Column(db.String, nullable=True)
    minHits = db.Column(db.String, nullable=True)
    maxHits = db.Column(db.String, nullable=True)
    ailment = db.Column(db.String, nullable=True)
    ailmentChance = db.Column(db.String, nullable=True)
    moveType = db.Column(db.String, nullable=True)
    critRate = db.Column(db.String, nullable=True)
    drain = db.Column(db.String, nullable=True)
    flinchChance = db.Column(db.String, nullable=True)
    healing = db.Column(db.String, nullable=True)
    maxTurns = db.Column(db.String, nullable=True)
    minTurns = db.Column(db.String, nullable=True)
    statChance = db.Column(db.String, nullable=True)
    damageClass = db.Column(db.String, nullable=True)
    accuracy = db.Column(db.String, nullable=True)
    effectChance = db.Column(db.String, nullable=True)
    priority = db.Column(db.String, nullable=True)
    pp = db.Column(db.String, nullable=True)
    target = db.Column(db.String, nullable=True)
    effect = db.Column(db.String, nullable=True)
    flavorText = db.Column(db.String, nullable=True)

    # Relationship to represent Pokemon that learn this move as a damage move
    damageMovesLearnedBy = relationship(
        "Pkmn", secondary=damageMovesLearnableByPokemon, back_populates="damageMoves"
    )

    # Relationship to represent Pokemon that learn this move as a status move
    statusMovesLearnedBy = relationship(
        "Pkmn", secondary=statusMovesLearnableByPokemon, back_populates="statusMoves"
    )

    def __init__(
        self,
        id,
        name,
        category,
        power,
        minHits,
        maxHits,
        ailment,
        ailmentChance,
        moveType,
        critRate,
        drain,
        flinchChance,
        healing,
        maxTurns,
        minTurns,
        statChance,
        damageClass,
        accuracy,
        effectChance,
        priority,
        pp,
        target,
        effect,
        flavorText,
    ):
        self.id = id
        self.name = name
        self.category = category
        self.power = power
        self.minHits = minHits
        self.maxHits = maxHits
        self.ailment = ailment
        self.ailmentChance = ailmentChance
        self.moveType = moveType
        self.critRate = critRate
        self.drain = drain
        self.flinchChance = flinchChance
        self.healing = healing
        self.maxTurns = maxTurns
        self.minTurns = minTurns
        self.statChance = statChance
        self.damageClass = damageClass
        self.accuracy = accuracy
        self.effectChance = effectChance
        self.priority = priority
        self.pp = pp
        self.target = target
        self.effect = effect
        self.flavorText = flavorText


class PkmnTeam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pkmnID = db.Column(db.Integer, db.ForeignKey("pkmn.id"), nullable=False)
    trainerID = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    shiny = db.Column(db.Boolean, nullable=False)
    chosenMove = db.Column(db.Integer, db.ForeignKey("pkmn_moves.id"), nullable=True)
    level = db.Column(db.Integer, nullable=True)
    position = db.Column(db.Integer, nullable=False)

    def __init__(self, pkmnID, trainerID, shiny, chosenMove, level, position):
        self.pkmnID = (pkmnID,)
        self.trainerID = trainerID
        self.shiny = shiny
        self.chosenMove = chosenMove
        self.level = level
        self.position = position


class UnownLetters(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    symbol = db.Column(db.String, nullable=False)
    sprite = db.Column(db.String, nullable=False)
    spriteShiny = db.Column(db.String, nullable=False)

    def __init__(self, letter, sprite, spriteShiny):
        self.symbol = letter
        self.sprite = sprite
        self.spriteShiny = spriteShiny


class BattleLog(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    battleID = db.Column(db.Integer, nullable=False)
    turnID = db.Column(db.Integer, nullable=False)
    playerID = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    enemyID = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    playerPkmnID = db.Column(db.Integer, db.ForeignKey("pkmn.id"), nullable=False)
    enemyPkmnID = db.Column(db.Integer, db.ForeignKey("pkmn.id"), nullable=False)
    playerPkmnHP = db.Column(db.Integer, nullable=False)
    enemyPkmnHP = db.Column(db.Integer, nullable=False)


class Battle(db.Models):
    id
    playerID
    enemyID


class Turn(db.Models):
    id
    battleID
    playerPkmn
    enemyPlayerPkmn
    playerPkmnHP
    enemyPlayerPkmnHP
