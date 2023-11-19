from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from app.validators import notEmpty, verifyAllowedInput
from flask_login import current_user
from app.models import PkmnTeam

class PokedexInputForm(FlaskForm):
    pokedexInput = StringField('See Pokémon Stats', validators=[notEmpty, verifyAllowedInput])
    favoritePkmnBtn = SubmitField('Choose Normal')
    favoriteShinyPkmnBtn = SubmitField('Choose Shiny')
    catchPkmnBtn = SubmitField('Throw a Poké Ball')
    sendToBoxBtn = SubmitField('Send To Box')
    deletePkmnBtn = SubmitField('Delete')
    cancelBtn = SubmitField('Cancel')
    battlePkmnBtn = SubmitField('Battle')
    enterGrassBtn = SubmitField('Enter Grass')

    def returnTeam(self, numInTeam=False):
        # team = [[pkmn.pkmnID, pkmn.shiny, pkmn.id] for pkmn in PkmnTeam.query.filter(PkmnTeam.trainerID == current_user.id).all()]
        team = [pkmn for pkmn in PkmnTeam.query.filter(PkmnTeam.trainerID == current_user.id).all()]
        if numInTeam == True:
            return len(team)
        else:
            return team