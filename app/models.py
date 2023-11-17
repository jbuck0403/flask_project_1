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

movesLearnableByPokemon = db.Table(
    'moves_learned_by_pokemon',
    db.Column('pkmn_id', db.Integer, db.ForeignKey('pkmn.id')),
    db.Column('move_id', db.Integer, db.ForeignKey('pkmn_moves.id'))
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
    moves = relationship('PkmnMoves', secondary=movesLearnableByPokemon, back_populates='knownBy')

    def __init__(self, id, name, sprite, spriteShiny, firstType, secondType, firstAbility, secondAbility, hiddenAbility, baseEXP, baseHP, baseAtk, baseDef, baseSpAtk, baseSpDef, baseSpd, form=False):
        self.id = id
        self.name = name
        self.sprite = sprite
        self.spriteShiny = spriteShiny
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
    power = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String, nullable=False)
    damageClass = db.Column(db.String, nullable=False)
    accuracy = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    pp = db.Column(db.Integer, nullable=False)
    flavorText = db.Column(db.String, nullable=False)
    knownBy = relationship('Pkmn', secondary=movesLearnableByPokemon, back_populates='moves')

    def __init__(self, id, name, power, type, damageClass, accuracy, priority, pp, flavorText):
        self.id = id
        self.name = name
        self.power = power
        self.type = type
        self.damageClass = damageClass
        self.accuracy = accuracy
        self.priority = priority
        self.pp = pp
        self.flavorText = flavorText

class PkmnTeam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pkmnID = db.Column(db.Integer, db.ForeignKey('pkmn.id'), nullable=False)
    trainerID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shiny = db.Column(db.Boolean, nullable=False)

    def __init__(self, pkmnID, trainerID, shiny):
        self.pkmnID = pkmnID,
        self.trainerID = trainerID
        self.shiny = shiny

class UnownLetters(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    symbol = db.Column(db.String, nullable=False)
    sprite = db.Column(db.String, nullable=False)
    spriteShiny = db.Column(db.String, nullable=False)

    def __init__(self, letter, sprite, spriteShiny):
        self.symbol = letter
        self.sprite = sprite
        self.spriteShiny = spriteShiny

