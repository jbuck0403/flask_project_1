from flask import request, render_template, flash, session
import requests
from .forms import PokedexInputForm
from app.models import db, PkmnTeam
from flask_login import current_user, login_required
from .Pokedex import Pokedex
from . import pokedexBP


@pokedexBP.route("/pokedex", methods=['GET', 'POST'])
def pokedex():
    form = PokedexInputForm()
    pokedex = Pokedex(form)

    if request.method == "POST" and form.validate_on_submit():

        pokemonData = pokedex.returnPokemonData(form)

        if isinstance(pokemonData, int):
            return pokedex.renderSprite(pokemonData, unownWord=True)
        else:
            pokemonInfoDict, spriteURL, spriteShinyURL = pokemonData

        if spriteURL != None:
            spriteResponse = requests.get(spriteURL)
        if spriteShinyURL != None:
            shinySpriteResponse = requests.get(spriteShinyURL)

        if  spriteURL == None or not spriteResponse.ok:
            return pokedex.render_pokedex(pokemonInfoDict=pokemonInfoDict.items())
        if  spriteShinyURL == None or not shinySpriteResponse.ok:
            return pokedex.render_pokedex(pokemonInfoDict=pokemonInfoDict.items(), spriteURL=spriteURL)

        return pokedex.render_pokedex(pokemonInfoDict=pokemonInfoDict.items(), spriteURL=spriteURL, spriteShinyURL=spriteShinyURL)
        
    
    return pokedex.render_pokedex()

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
            if not isinstance(pokemonData, int):
                name, pokedexID, sprite, shinySprite = pokemonData
            else:
                sprite = pokemonData
            form.pokedexInput.data = ""
            if isinstance(sprite, int):
                unownWord = pokedex.unownSpeller()
                if isinstance(unownWord[0], int):
                    return render_template("favorite.jinja", form=form, errorCode=unownWord[0])
                return render_template("favorite.jinja", form=form, unownWord=unownWord)
            
            session['pokedexID'] = pokedexID
            
            return render_template("favorite.jinja", form=form, spriteURL=sprite, shinySpriteURL=shinySprite, name=name)

    return render_template("favorite.jinja", form=form)

@pokedexBP.route('/catch', methods=['GET','POST'])
@login_required
def catch():
    form = PokedexInputForm()
    pokedex = Pokedex(form)
    form.pokedexInput.label.text = "Catch Pokémon"

    if request.method == "POST":
        if "catchPkmnBtn" in request.form:
            if form.returnTeam(numInTeam=True) < 6:
                pokedexID = session.pop('pokedexID')
                shiny = session.pop('shiny')
                name = session.pop('name')
                
                try:
                    newPkmn = PkmnTeam(pokedexID, current_user.id, shiny)
                    db.session.add(newPkmn)
                    db.session.commit()
                    flash(f"{name} caught!", "success")
                except:
                    db.session.rollback()
                    flash(f"Error catching {name}...", "error")
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
                unownWord = pokedex.unownSpeller()
                if isinstance(unownWord[0], int):
                    return render_template("catch.jinja", form=form, errorCode=unownWord[0])
                return render_template("catch.jinja", form=form, unownWord=unownWord)
            
            session['pokedexID'] = pokedexID
            session['shiny'] = shiny
            session['name'] = name
            
            return render_template("catch.jinja", form=form, spriteURL=sprite, name=name)

    return render_template("catch.jinja", form=form)

@pokedexBP.route('/team', methods=['GET','POST'])
@login_required
def team():
    form = PokedexInputForm()
    pokedex = Pokedex(form)
    pkmnTeam = form.returnTeam()
    pkmnTeamURLS = [pokedex.returnSpriteURL(pkmn[0], "pokemon", pkmn[1]) for pkmn in pkmnTeam]

    if request.method == 'POST':
        if 'sendToBoxBtn' in request.form:
            
            if request.form.get('sendToBoxBtn').strip().isdigit():
            
                index = int(request.form.get('sendToBoxBtn').strip()) - 1

                try:
                    pkmnToDelete = PkmnTeam.query.filter(PkmnTeam.id == pkmnTeam[index][2]).first()
                    db.session.delete(pkmnToDelete)
                    db.session.commit()
                    flash("Successfully sent Pokémon to Box!", "success")
                    pkmnTeam = form.returnTeam()
                    pkmnTeamURLS = [pokedex.returnSpriteURL(pkmn[0], "pokemon", pkmn[1]) for pkmn in pkmnTeam]
                except:
                    db.session.rollback()
                    flash("Error sending Pokémon to Box...", "error")

            return render_template('team.jinja', form=form, pkmnTeam=pkmnTeamURLS, sendingToBox=True)

    return render_template('team.jinja', form=form, pkmnTeam=pkmnTeamURLS)