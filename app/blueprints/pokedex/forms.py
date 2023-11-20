from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from app.validators import notEmpty, verifyAllowedInput
from flask_login import current_user
from app.models import PkmnTeam, db, User, Pkmn
from flask import flash
from sqlalchemy import asc, func


class PokedexInputForm(FlaskForm):
    pokedexInput = StringField(
        "See Pokémon Stats", validators=[notEmpty, verifyAllowedInput]
    )
    favoritePkmnBtn = SubmitField("Choose Normal")
    favoriteShinyPkmnBtn = SubmitField("Choose Shiny")


class PartyForm(FlaskForm):
    sendToBoxBtn = SubmitField("Send To Box")
    deletePkmnBtn = SubmitField("Delete")
    cancelBtn = SubmitField("Cancel")
    battlePkmnBtn = SubmitField("Battle")
    enterGrassBtn = SubmitField("Enter Grass")
    setPartyLeaderBtn = SubmitField("Set Party Leader")
    reorderBtn = SubmitField("Reorder")
    catchPkmnBtn = SubmitField("Throw a Poké Ball")
    nextBattleBtn = SubmitField("Continue")

    def returnTeam(self, numInTeam=False, enemyID=False):
        team = (
            PkmnTeam.query.filter_by(trainerID=enemyID if enemyID else current_user.id)
            .order_by(asc(PkmnTeam.position))
            .all()
        )

        if numInTeam == True:
            return len(team)
        else:
            return team

    def returnEnemyTeam(self, trainerID):
        team = (
            PkmnTeam.query.filter_by(trainerID=trainerID)
            .order_by(asc(PkmnTeam.position))
            .all()
        )

    def swapPkmnPosition(self, idxToSwap, swappingTo=0):
        """default value for swappingTo swaps pokemon at idxToSwap position with current party leader"""
        pokemonInTeam = self.returnTeam()

        if pokemonInTeam:
            try:
                swappingPkmnPosition = pokemonInTeam[idxToSwap].position
                swappedPkmnPosition = pokemonInTeam[swappingTo].position

                pokemonInTeam[idxToSwap].position = swappedPkmnPosition
                pokemonInTeam[swappingTo].position = swappingPkmnPosition

                db.session.commit()
                flash("Successfully changed party leader!", "success")
            except:
                db.session.rollback()
                flash("Error changing party leader...", "error")
        else:
            flash("Party is empty...")

    def removeFromTeam(self, idxToRemove):
        try:
            pkmnInTeam = self.returnTeam()
            pkmnToDelete = pkmnInTeam.pop(idxToRemove)

            for idx, pkmn in enumerate(pkmnInTeam):
                if idx == 0:
                    pkmn.position = 1
                else:
                    pkmn.position = pkmnInTeam[idx - 1].position + 1

            db.session.delete(pkmnToDelete)
            db.session.commit()
            flash("Successfully sent Pokémon to Box!", "success")

        except:
            db.session.rollback()
            flash("Error sending Pokémon to Box...", "error")

    def returnAllTeamsWithPkmn(self, excludeCurrentUser=True):
        # Function to find unique trainerIDs and associated User names
        def findUniqueTrainerIDsAndNames():
            query = db.session.query(PkmnTeam.trainerID, User.userName).distinct()
            query = query.join(User, PkmnTeam.trainerID == User.id)
            if excludeCurrentUser:
                query = query.filter(PkmnTeam.trainerID != current_user.id)
            return query.all()

        # Get unique trainerIDs and associated User names
        uniqueTrainerIDsAndNames = findUniqueTrainerIDsAndNames()

        # Dictionary to store teams with User names as keys
        allTeamsWithPkmn = {}

        # Retrieve teams and associated Pkmn for each unique trainerID
        for id, name in uniqueTrainerIDsAndNames:
            teamsWithPkmn = (
                db.session.query(PkmnTeam, Pkmn)
                .filter(PkmnTeam.trainerID == id)
                .join(Pkmn, PkmnTeam.pkmnID == Pkmn.id)
                .order_by(asc(PkmnTeam.position))
                .all()
            )

            allTeamsWithPkmn[name] = teamsWithPkmn

        breakpoint()
        return allTeamsWithPkmn
