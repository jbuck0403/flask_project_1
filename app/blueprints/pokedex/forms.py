from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from app.validators import notEmpty, verifyAllowedInput

class PokedexInputForm(FlaskForm):
    pokedexInput = StringField('Enter Pokémon', validators=[notEmpty, verifyAllowedInput])
    favoritePkmn = SubmitField('Choose Normal')
    favoriteShinyPkmn = SubmitField('Choose Shiny')