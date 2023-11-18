from flask import request, render_template, flash, session, redirect, url_for
import requests
from .forms import PokedexInputForm
from app.models import db, PkmnTeam, damageMovesLearnableByPokemon, PkmnMoves, Pkmn
from flask_login import current_user, login_required
from .Pokedex import Pokedex
from . import pokedexBP
from sqlalchemy.sql import func
import random


@pokedexBP.route('/moves', methods=['GET','POST'])
def moves():
    form = PokedexInputForm()
    pokedex = Pokedex(form)

    form.pokedexInput.label.text = "Search Move"

    if request.method == "POST" and form.validate_on_submit():

        moveData = pokedex.returnPokemonMove(form)
        form.pokedexInput.data = ""
        if isinstance(moveData, int):
            return pokedex.unownMessage(form, True, 'moves.jinja')
        else:
            return render_template('moves.jinja', form=form, moveData=moveData.items())
    
    return render_template('moves.jinja', form=form)
            


@pokedexBP.route("/pokedex", methods=['GET', 'POST'])
def pokedex():
    def render_pokedex(**kwargs):
        form.pokedexInput.data = ""
        return render_template('pokedex.jinja', form=form, **kwargs)
    
    form = PokedexInputForm()
    pokedex = Pokedex(form)

    if request.method == "POST" and form.validate_on_submit():

        pokemonData = pokedex.returnPokemonData(form)
        if isinstance(pokemonData, int):
            form.pokedexInput.data = ""
            return pokedex.unownMessage(form, True, 'pokedex.jinja')
        else:
            pokemonInfoDict, spriteURL, spriteShinyURL = pokemonData

        if spriteURL != None:
            spriteResponse = requests.get(spriteURL)
        if spriteShinyURL != None:
            shinySpriteResponse = requests.get(spriteShinyURL)

        if  spriteURL == None or not spriteResponse.ok:
            return render_pokedex(pokemonInfoDict=pokemonInfoDict.items())
        if  spriteShinyURL == None or not shinySpriteResponse.ok:
            return render_pokedex(pokemonInfoDict=pokemonInfoDict.items(), spriteURL=spriteURL)

        return render_pokedex(pokemonInfoDict=pokemonInfoDict.items(), spriteURL=spriteURL, spriteShinyURL=spriteShinyURL)
        
    
    return render_pokedex()

@pokedexBP.route("/favorite", methods=['GET', 'POST'])
@login_required
def favorite():
    form = PokedexInputForm()
    pokedex = Pokedex(form)
    form.pokedexInput.label.text = "Choose Favorite Pokémon"
    
    if request.method == "POST":
        if "favoritePkmnBtn" in request.form or "favoriteShinyPkmnBtn" in request.form:
            pokedexID = session.pop('pokedexID', current_user.userName)
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
            pokemonData = pokedex.returnPokemonData(form, favorite=True)
            form.pokedexInput.data = ""
            if not isinstance(pokemonData, int):
                name, pokedexID, sprite, shinySprite = pokemonData
            else:
                # sprite = pokemonData
                return pokedex.unownMessage(form, True, "favorite.jinja")
            
            session['pokedexID'] = pokedexID
            return render_template("favorite.jinja", form=form, spriteURL=sprite, shinySpriteURL=shinySprite, name=name)
    form.pokedexInput.data = ""
    return render_template("favorite.jinja", form=form)

@pokedexBP.route('/remove_favorite')
@login_required
def remove_favorite():
    try:
        current_user.favoritePkmn = None
        db.session.commit()
        flash("Favorite set to default", "success")
    except:
        db.session.rollback()
        flash("Error setting default favorite...", "error")
    
    return redirect(url_for('pokedexBP.favorite'))

@pokedexBP.route('/catch', methods=['GET','POST'])
@login_required
def catch():
    form = PokedexInputForm()
    pokedex = Pokedex(form)
    form.pokedexInput.label.text = "Catch Pokémon"

    if request.method == "POST":
        if "catchPkmnBtn" in request.form:
            pokedexID = session.pop('pokedexID')
            shiny = session.pop('shiny')
            name = session.pop('name')
            trainerPkmn = [pkmn.pkmnID for pkmn in PkmnTeam.query.filter(PkmnTeam.trainerID == current_user.id).all()]
           
            if form.returnTeam(numInTeam=True) < 6 and not pokedexID in trainerPkmn:
            
                filteredQuery = (
                    db.session.query(damageMovesLearnableByPokemon)
                    .join(PkmnMoves)
                    .filter(PkmnMoves.effect == 'Inflicts regular damage.')
                    .order_by(func.random())
                    .limit(1)
                    .first()
                )
                try:
                    newPkmn = PkmnTeam(pokedexID, current_user.id, shiny, filteredQuery.move_id, 1)
                    db.session.add(newPkmn)
                    db.session.commit()
                    flash(f"{name} caught!", "success")
                except Exception as e:
                    db.session.rollback()
                    flash(f"Error catching {name}...{e}", "error")
            else:
                if pokedexID in trainerPkmn:
                    flash(f"Team already has a {name}...", "warning")
                else:
                    flash("Team is full...", "warning")

        elif "pokedexInput" in request.form and form.validate_on_submit():
            pokemonData = pokedex.returnPokemonData(form, catch=True)
            if not isinstance(pokemonData, int):
                name, pokedexID, sprite, shiny = pokemonData
            else:
                sprite = pokemonData

            form.pokedexInput.data = ""
            if isinstance(sprite, int):
                return pokedex.unownMessage(form, True, "catch.jinja")
            
            session['pokedexID'] = pokedexID
            session['shiny'] = shiny
            session['name'] = name
            
            return render_template("catch.jinja", form=form, spriteURL=sprite, name=name)
    form.pokedexInput.data = ""    
    return render_template("catch.jinja", form=form)

@pokedexBP.route('/team', methods=['GET','POST'])
@login_required
def team():
    def returnTailoredPkmnObj():
        pokemonFromTeam = form.returnTeam()
        pkmnObjects = [Pkmn.query.get(pkmn.pkmnID) for pkmn in pokemonFromTeam]
        pkmnTeamURLS = [pokedex.returnPokemonData(pkmn.pkmnID, team=True, shiny=pkmn.shiny) for pkmn in pokemonFromTeam]
        for idx, pkmn in enumerate(pkmnTeamURLS):
            print(pkmnObjects[idx].id)
            pkmnObjects[idx].spriteToDisplay = pkmn
            pkmnObjects[idx].combinedType = f"{pkmnObjects[idx].firstType}/{pkmnObjects[idx].secondType}"
            pkmnObjects[idx].move = pokedex.titlePokemon(PkmnMoves.query.get(pokemonFromTeam[idx].chosenMove).name)

        return pkmnObjects
    
    form = PokedexInputForm()
    pokedex = Pokedex(form)
    pkmnObjects = returnTailoredPkmnObj()
    
    if request.method == 'POST':
        if 'deletePkmnBtn' in request.form:
            
            index = int(request.form.get('deletePkmnBtn').strip()) - 1
            print(index)
            try:
                pkmnToDelete = PkmnTeam.query.filter(PkmnTeam.pkmnID == pkmnObjects[index].id).first()
                db.session.delete(pkmnToDelete)
                db.session.commit()
                flash("Successfully sent Pokémon to Box!", "success")
                pkmnObjects = returnTailoredPkmnObj()
                
            except:
                db.session.rollback()
                flash("Error sending Pokémon to Box...", "error")

        elif 'cancelBtn' in request.form:
            return render_template('team.jinja', form=form, pkmnTeam=pkmnObjects, instantSprite=True)
        

        return render_template('team.jinja', form=form, pkmnTeam=pkmnObjects, sendingToBox=True)
   
    return render_template('team.jinja', form=form, pkmnTeam=pkmnObjects)



