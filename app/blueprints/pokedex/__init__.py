from flask import Blueprint

pokedexBP = Blueprint('pokedexBP', __name__, template_folder='pokedex_templates')

from app.blueprints.pokedex import routes