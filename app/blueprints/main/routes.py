from flask import render_template, flash
from flask_login import current_user
from ..pokedex.Pokedex import Pokedex
from . import main
from app.models import db, PkmnMoves, Pkmn, damageMovesLearnableByPokemon

@main.route("/", methods=['GET', 'POST'])
def landingPage():
    pokedex = Pokedex()
    
    return pokedex.unownMessage(None, "welcome",'landingPage.jinja')