from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from app.validators import notEmpty, verifyAllowedInput
from flask_login import current_user
from app.models import PkmnTeam

class PokedexInputForm(FlaskForm):
    pokedexInput = StringField('See Pokémon Stats', validators=[notEmpty, verifyAllowedInput])
    favoritePkmn = SubmitField('Choose Normal')
    favoriteShinyPkmn = SubmitField('Choose Shiny')
    catchPkmn = SubmitField('Throw a Poké Ball')
    sendToBox = SubmitField('Send To Box')

    def returnTeam(self, numInTeam=False):
        team = [[pkmn.pkmnID, pkmn.shiny] for pkmn in PkmnTeam.query.filter(PkmnTeam.trainerID == current_user.id).all()]
        print(team)
        if numInTeam == True:
            return len(team)
        else:
            return team