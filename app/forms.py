from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class PokedexInputForm(FlaskForm):
    pokedexInput = StringField('Enter Pokémon', validators=[DataRequired()])