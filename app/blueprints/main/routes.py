from flask import render_template
from flask_login import current_user
from ..pokedex.Pokedex import Pokedex
from . import main

@main.route("/", methods=['GET', 'POST'])
def landingPage():
    pokedex = Pokedex()

    return render_template('landingPage.jinja', unownWord=pokedex.unownSpeller("welcome"))