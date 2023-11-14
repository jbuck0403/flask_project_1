from flask import request, render_template, flash, session
import requests
from .forms import PokedexInputForm
from app.models import db
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

        print(spriteURL)
        return pokedex.render_pokedex(pokemonInfoDict=pokemonInfoDict.items(), spriteURL=spriteURL, spriteShinyURL=spriteShinyURL)
        
    
    return pokedex.render_pokedex()

@pokedexBP.route("/favorite", methods=['GET', 'POST'])
@login_required
def favorite():
    form = PokedexInputForm()
    pokedex = Pokedex(form)

    if request.method == "POST":
        if "favoritePkmn" in request.form or "favoriteShinyPkmn" in request.form:
            pokedexID = session.pop('pokedexID', current_user.userName)
            shiny = False
            if "favoriteShinyPkmn" in request.form:
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