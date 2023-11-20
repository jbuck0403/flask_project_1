from flask import request, render_template, flash, session, redirect, url_for
import requests
from .forms import PokedexInputForm, PartyForm
from app.models import db, PkmnTeam, damageMovesLearnableByPokemon, PkmnMoves, Pkmn
from flask_login import current_user, login_required
from .Pokedex import Pokedex
from . import pokedexBP
from sqlalchemy.sql import func, desc, asc
import random
from .battle import PokemonBattle


@pokedexBP.route("/moves", methods=["GET", "POST"])
def moves():
    form = PokedexInputForm()
    pokedex = Pokedex(form)

    form.pokedexInput.label.text = "Search Move"

    if request.method == "POST" and form.validate_on_submit():
        moveData = pokedex.returnPokemonMove(form)
        form.pokedexInput.data = ""
        if isinstance(moveData, int):
            return pokedex.unownMessage(form, True, "moves.jinja")
        else:
            return render_template("moves.jinja", form=form, moveData=moveData.items())

    return render_template("moves.jinja", form=form)


@pokedexBP.route("/pokedex", methods=["GET", "POST"])
def pokedex():
    def render_pokedex(**kwargs):
        form.pokedexInput.data = ""
        return render_template("pokedex.jinja", form=form, **kwargs)

    form = PokedexInputForm()
    pokedex = Pokedex(form)

    if request.method == "POST" and form.validate_on_submit():
        pokemonData = pokedex.returnPokemonInfoDict(form)

        if isinstance(pokemonData, int):
            form.pokedexInput.data = ""
            return pokedex.unownMessage(form, True, "pokedex.jinja")
        else:
            pokemonInfoDict, spriteURL, spriteShinyURL = pokemonData

        if spriteURL != None:
            spriteResponse = requests.get(spriteURL)
        if spriteShinyURL != None:
            shinySpriteResponse = requests.get(spriteShinyURL)

        if spriteURL == None or not spriteResponse.ok:
            return render_pokedex(pokemonInfoDict=pokemonInfoDict.items())
        if spriteShinyURL == None or not shinySpriteResponse.ok:
            return render_pokedex(
                pokemonInfoDict=pokemonInfoDict.items(), spriteURL=spriteURL
            )

        return render_pokedex(
            pokemonInfoDict=pokemonInfoDict.items(),
            spriteURL=spriteURL,
            spriteShinyURL=spriteShinyURL,
        )

    return render_pokedex()


@pokedexBP.route("/favorite", methods=["GET", "POST"])
@login_required
def favorite():
    form = PokedexInputForm()
    pokedex = Pokedex(form)
    form.pokedexInput.label.text = "Choose Favorite Pokémon"

    if request.method == "POST":
        if "favoritePkmnBtn" in request.form or "favoriteShinyPkmnBtn" in request.form:
            pokedexID = session.pop("pokedexID", current_user.userName)
            shiny = False
            if "favoriteShinyPkmnBtn" in request.form:
                shiny = True

            try:
                current_user.favoritePkmn = f"{pokedexID},{'s' if shiny else 'd'}"
                db.session.commit()
                flash("Favorite successfully assigned!", "success")
            except:
                db.session.rollback()
                flash("Error assigning favorite...", "error")

        elif "pokedexInput" in request.form and form.validate_on_submit():
            pokemonData = pokedex.returnPokemonObj(form)
            print(pokemonData)
            form.pokedexInput.data = ""
            if not isinstance(pokemonData, int):
                name, pokedexID, sprite, shinySprite = (
                    pokemonData.name,
                    pokemonData.id,
                    pokemonData.sprite,
                    pokemonData.spriteShiny,
                )
            else:
                return pokedex.unownMessage(form, True, "favorite.jinja")

            session["pokedexID"] = pokedexID
            return render_template(
                "favorite.jinja",
                form=form,
                spriteURL=sprite,
                shinySpriteURL=shinySprite,
                name=name,
            )
    form.pokedexInput.data = ""
    return render_template("favorite.jinja", form=form)


@pokedexBP.route("/remove_favorite")
@login_required
def remove_favorite():
    try:
        current_user.favoritePkmn = None
        db.session.commit()
        flash("Favorite set to default", "success")
    except:
        db.session.rollback()
        flash("Error setting default favorite...", "error")

    return redirect(url_for("pokedexBP.favorite"))


@pokedexBP.route("/tall_grass", methods=["GET", "POST"])
@login_required
def tallGrass():
    form = PartyForm()
    pokedex = Pokedex(form)

    if request.method == "POST":
        if "enterGrassBtn" not in request.form:
            try:
                pkmnID = session.pop("pkmnID")
            except Exception as e:
                print(e)

            sprite = session.pop("spriteURL")
            name = session.pop("name")
            shiny = session.pop("shiny")
            trainerPkmn = form.returnTeam()
            canCatch = form.returnTeam(numInTeam=True) < 6 and not pkmnID in trainerPkmn

            if "battlePkmnBtn" in request.form:
                return redirect(url_for("pokedexBP.battle", pkmnID=pkmnID, trainerID=0))

            elif "catchPkmnBtn" in request.form:
                if canCatch:
                    move = randomPkmnMove(pkmnID)

                    try:
                        highestPosition = (
                            PkmnTeam.query.filter_by(trainerID=current_user.id)
                            .order_by(desc(PkmnTeam.position))
                            .first()
                        )

                        if highestPosition == None:
                            nextPosition = 1
                        else:
                            nextPosition = highestPosition.position + 1

                        newPkmn = PkmnTeam(
                            pkmnID,
                            current_user.id,
                            shiny,
                            move.move_id,
                            1,
                            nextPosition,
                        )

                        db.session.add(newPkmn)
                        db.session.commit()
                        flash(f"{name} caught!", "success")
                    except Exception as e:
                        db.session.rollback()
                        flash(f"Error catching {name}...{e}", "error")
                else:
                    if pkmnID in trainerPkmn:
                        flash(f"Team already has a {name}...", "warning")
                    else:
                        flash("Team is full...", "warning")
                    return render_template(
                        "tallGrass.jinja",
                        form=form,
                        spriteURL=sprite,
                        canCatch=canCatch,
                    )

                return render_template("tallGrass.jinja", form=form)

        else:
            lastPkmnIdx = 1017
            randomPkmn = random.randint(1, lastPkmnIdx + 1)
            pkmnObj = pokedex.returnPokemonObj(randomPkmn)

            if pkmnObj:
                pkmnObj = pokedex.randomShinyChance(pkmnObj)

                session["pkmnID"] = pkmnObj.id
                session["shiny"] = pkmnObj.shiny
                session["name"] = pkmnObj.name
                session["spriteURL"] = pkmnObj.chosenSprite
                trainerPkmn = form.returnTeam()

                canCatch = (
                    form.returnTeam(numInTeam=True) < 6
                    and not pkmnObj.id in trainerPkmn
                )
                canBattle = True if form.returnTeam(numInTeam=True) > 0 else False

                return render_template(
                    "tallGrass.jinja",
                    form=form,
                    spriteURL=pkmnObj.chosenSprite,
                    name=pkmnObj.name,
                    canCatch=canCatch,
                    canBattle=canBattle,
                )

            else:
                flash("Error getting Pokémon...", "error")

    return render_template("tallGrass.jinja", form=form)


@pokedexBP.route("/battle/<int:pkmnID><int:trainerID>", methods=["GET", "POST"])
@login_required
def battle(pkmnID, trainerID):
    form = PartyForm()
    match = PokemonBattle()

    previousRoute = request.headers.get("Referer")
    if previousRoute != None:
        previousRoute = previousRoute.split("/")
        previousRoute = previousRoute[len(previousRoute) - 1]

    team = form.returnTeam()
    if team:
        playerPkmn = Pkmn.query.get(team[0].pkmnID)
        playerPkmn.level = team[0].level
        playerPkmn.move = PkmnMoves.query.get(team[0].chosenMove)

        enemyPkmn = Pkmn.query.filter(Pkmn.id == pkmnID).first()
        if trainerID == 0:
            enemyPkmn.level = team[0].level
            enemyPkmn.move = PkmnMoves.query.filter(
                PkmnMoves.id == randomPkmnMove(pkmnID)[1]
            ).first()
        else:
            enemyTeam = form.returnTeam(enemyID=trainerID)

        outcome, winner = match.battle(playerPkmn, enemyPkmn)
        winnerRemainingHP = winner.scaledHP
        session["winnerRemainingHP"] = winnerRemainingHP
        breakpoint()

        if previousRoute == "tall_grass":
            nextRoute = url_for("pokedexBP.tallGrass")
        else:
            nextRoute = url_for("pokedexBP.battleTower")

        return render_template(
            "battle.jinja",
            form=form,
            playerPkmn=playerPkmn,
            enemyPkmn=enemyPkmn,
            outcome=outcome,
            nextRoute=nextRoute,
        )
    else:
        flash("Team is currently empty...", "warning")
        return redirect(url_for("pokedexBP.tallGrass"))


def randomPkmnMove(pkmnID):
    move = (
        db.session.query(damageMovesLearnableByPokemon)
        .join(PkmnMoves)
        .filter(damageMovesLearnableByPokemon.c.pkmn_id == pkmnID)
        .filter(PkmnMoves.effect == "Inflicts regular damage.")
        .order_by(func.random())
        .limit(1)
        .first()
    )
    return move


@pokedexBP.route("/team", methods=["GET", "POST"])
@login_required
def team():
    def returnTailoredPkmnObj():
        pokemonFromTeam = form.returnTeam()
        pkmnObjects = [Pkmn.query.get(pkmn.pkmnID) for pkmn in pokemonFromTeam]
        pkmnTeamURLS = [
            pokedex.returnPokemonSprite(pkmn.pkmnID, shiny=pkmn.shiny)
            for pkmn in pokemonFromTeam
        ]

        for idx, pkmn in enumerate(pkmnTeamURLS):
            pkmnObjects[idx].spriteToDisplay = pkmn
            pkmnObjects[
                idx
            ].combinedType = f"{pkmnObjects[idx].firstType}{'/' + pkmnObjects[idx].secondType if pkmnObjects[idx].secondType != 'None' else ''}"
            pkmnObjects[idx].move = pokedex.titlePokemon(
                PkmnMoves.query.get(pokemonFromTeam[idx].chosenMove).name
            )
            pkmnObjects[idx].moveType = pokedex.titlePokemon(
                PkmnMoves.query.get(pokemonFromTeam[idx].chosenMove).moveType
            )
            pkmnObjects[
                idx
            ].nameAndType = f"{pkmnObjects[idx].name} [{pkmnObjects[idx].combinedType}]"
            pkmnObjects[
                idx
            ].moveAndType = f"{pkmnObjects[idx].move} [{pkmnObjects[idx].moveType}]"

        return pkmnObjects

    form = PartyForm()
    pokedex = Pokedex(form)
    pkmnObjects = returnTailoredPkmnObj()

    if request.method == "POST":
        print(request.form)
        if "reorderBtn" in request.form:
            index = int(request.form.get("reorderBtn").strip()) - 1
            form.swapPkmnPosition(index)
            pkmnObjects = returnTailoredPkmnObj()

            return render_template(
                "team.jinja", form=form, pkmnTeam=pkmnObjects, reordering=True
            )

        elif "deletePkmnBtn" in request.form:
            index = int(request.form.get("deletePkmnBtn").strip()) - 1
            form.removeFromTeam(index)
            pkmnObjects = returnTailoredPkmnObj()

            return render_template(
                "team.jinja", form=form, pkmnTeam=pkmnObjects, sendingToBox=True
            )

        elif "cancelBtn" in request.form:
            return render_template(
                "team.jinja", form=form, pkmnTeam=pkmnObjects, instantSprite=True
            )

        elif "setPartyLeaderBtn" in request.form:
            return render_template(
                "team.jinja", form=form, pkmnTeam=pkmnObjects, reordering=True
            )

        elif "sendToBoxBtn" in request.form:
            return render_template(
                "team.jinja", form=form, pkmnTeam=pkmnObjects, sendingToBox=True
            )

    return render_template("team.jinja", form=form, pkmnTeam=pkmnObjects)


@pokedexBP.route("/battle_tower")
@login_required
def battleTower():
    form = PartyForm()
    allTeams = form.returnAllTeamsWithPkmn()

    return render_template("battleTower.jinja", allTeams=allTeams)


# @pokedexBP.route('/catch_pokemon/<int:pkmnID>/<bool:shiny>')
# @login_required
# def catchPokemon(pkmnID, shiny):
#     form = PokedexInputForm()
#     pokedex = Pokedex(form)
#     pkmnObj = pokedex.returnPokemonData(pkmnID, grass=True, foundInGrass=True, shintDecidedshiny=shiny)
#     print("from catchPokemon",pkmnObj)
#     trainerPkmn = [pkmn.pkmnID for pkmn in PkmnTeam.query.filter(PkmnTeam.trainerID == current_user.id).all()]
#     pkmnID = pkmnObj.id
#     name = pkmnObj.name
#     move = randomPkmnMove(pkmnID)

#     if form.returnTeam(numInTeam=True) < 6 and not pkmnID in trainerPkmn:

#                 move = randomPkmnMove()
#                 try:

#                     newPkmn = PkmnTeam(pkmnID, current_user.id, pkmnObj.shiny, move.move_id, 1)
#                     db.session.add(newPkmn)
#                     db.session.commit()
#                     flash(f"{name} caught!", "success")
#                 except Exception as e:
#                     db.session.rollback()
#                     flash(f"Error catching {name}...{e}", "error")
#     else:
#         if pkmnID in trainerPkmn:
#             flash(f"Team already has a {name}...", "warning")
#         else:
#             flash("Team is full...", "warning")

#     return redirect(url_for('pokedexBP.tallGrass'))

# @pokedexBP.route('/battle_pokemon/<int:pkmn_id>')
# @login_required
# def battlePokemon(pkmn_id):
#     pass

# @pokedexBP.route('/catch', methods=['GET','POST'])
# @login_required
# def catch():
#     form = PokedexInputForm()
#     pokedex = Pokedex(form)
#     form.pokedexInput.label.text = "Catch Pokémon"

#     if request.method == "POST":
#         if "catchPkmnBtn" in request.form:
#             pokedexID = session.pop('pokedexID')
#             shiny = session.pop('shiny')
#             name = session.pop('name')
#             trainerPkmn = [pkmn.pkmnID for pkmn in PkmnTeam.query.filter(PkmnTeam.trainerID == current_user.id).all()]

#             if form.returnTeam(numInTeam=True) < 6 and not pokedexID in trainerPkmn:

#                 move = randomPkmnMove(pokedexID)

#                 try:
#                     newPkmn = PkmnTeam(pokedexID, current_user.id, shiny, move.move_id, 1)
#                     db.session.add(newPkmn)
#                     db.session.commit()
#                     flash(f"{name} caught!", "success")
#                 except Exception as e:
#                     db.session.rollback()
#                     flash(f"Error catching {name}...{e}", "error")
#             else:
#                 if pokedexID in trainerPkmn:
#                     flash(f"Team already has a {name}...", "warning")
#                 else:
#                     flash("Team is full...", "warning")

#         elif "pokedexInput" in request.form and form.validate_on_submit():
#             pokemonData = pokedex.returnPokemonData(form, catch=True)
#             if not isinstance(pokemonData, int):
#                 name, pokedexID, sprite, shiny = pokemonData
#             else:
#                 sprite = pokemonData

#             form.pokedexInput.data = ""
#             if isinstance(sprite, int):
#                 return pokedex.unownMessage(form, True, "catch.jinja")

#             session['pokedexID'] = pokedexID
#             session['shiny'] = shiny
#             session['name'] = name

#             return render_template("catch.jinja", form=form, spriteURL=sprite, name=name)
#         elif "battlePkmnBtn" in request.form:
#             pass

#     form.pokedexInput.data = ""
#     return render_template("catch.jinja", form=form)
