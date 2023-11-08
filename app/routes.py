from flask import request, render_template, redirect
import requests
from app import app
from app.forms import PokedexInputForm

@app.route("/", methods=['GET', 'POST'])
def landingPage():
    if request.method == "POST":
        #return render_template('displayPokemon.jinja')
        return redirect("/pokedex")
    else:
        return render_template('landingPage.jinja')

@app.route("/pokedex", methods=['GET', 'POST'])
def displayPokemon():
    def returnDitto(errorCode):
        url = f"https://pokeapi.co/api/v2/pokemon/ditto"
        response = requests.get(url)

        if not response.ok:
            return render_template('displayPokemon.jinja', connectErrorCode=response.status_code, form=form)

        data = response.json()
        sprite = data['sprites']['front_default']
        return render_template('displayPokemon.jinja', errorCode=errorCode, sprite=sprite, form=form)

    form = PokedexInputForm()

    if request.method == "POST" and form.validate_on_submit():

        id = form.pokedexInput.data

        url = f"https://pokeapi.co/api/v2/pokemon/{id}"
        response = requests.get(url)

        errorCode = response.status_code
        
        if not response.ok:
            return returnDitto(errorCode)
            
        else:
            data = response.json()
            print(data['sprites']['front_default'])

            name = data['name'].title()
            abilities = [ability['ability']['name'].title() for ability in data['abilities'] if ability['is_hidden'] == False]
            try:
                hiddenAbility = [ability['ability']['name'].title() for ability in data['abilities'] if ability['is_hidden'] == True][0]
            except:
                hiddenAbility = 'None'

            baseExp = data['base_experience']
            spriteURL = data['sprites']['front_default']
            spriteShinyURL = data['sprites']['front_shiny']
            baseStats = {stat['stat']['name'].upper() + ':': stat['base_stat'] for stat in data['stats']}
            pokemonType = [pkmnType['type']['name'].title() for pkmnType in data['types']]
            pokedexID = data['id']

            pokemonType = f"{pokemonType[0]}{'/' + pokemonType[1] if len(pokemonType) > 1 else ''}"

            labels = ["Name:", "ID:", "Type:", "Ability 1:", "Ability 2:", "Hidden Ability:", "Base Exp:"] + list(baseStats.keys())
            pkmnInfo = [name, pokedexID, pokemonType, abilities[0], abilities[1] if len(abilities) > 1 else 'None', hiddenAbility, baseExp] + list(baseStats.values())

            pokemonInfoDict = dict(zip(labels, pkmnInfo))

            spriteResponse = requests.get(spriteURL)
            shinySpriteResponse = requests.get(spriteShinyURL)

            if not spriteResponse.ok:
                return render_template('displayPokemon.jinja', pokemonInfoDict=pokemonInfoDict.items(), form=form)
            if not shinySpriteResponse.ok:
                return render_template('displayPokemon.jinja', pokemonInfoDict=pokemonInfoDict.items(), spriteURL=spriteURL, form=form)

            return render_template('displayPokemon.jinja', pokemonInfoDict=pokemonInfoDict.items(), spriteURL=spriteURL, spriteShinyURL=spriteShinyURL, form=form)
        
    else:
        return render_template('displayPokemon.jinja', form=form)