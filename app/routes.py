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
    def render_pokedex(**kwargs):
        form.pokedexInput.data = ""
        return render_template('displayPokemon.jinja', form=form, bulbaNameURL=bulbaNameURL, **kwargs)

    def returnDitto(errorCode):
        url = f"https://pokeapi.co/api/v2/pokemon/ditto"
        response = requests.get(url)

        if not response.ok:

            return render_pokedex(connectErrorCode=response.status_code)

        data = response.json()
        sprite = data['sprites']['front_default']

        return render_pokedex(errorCode=errorCode, sprite=sprite)

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

            bulbaNameURL = f"https://bulbapedia.bulbagarden.net/wiki/{name}_(Pok%C3%A9mon)"

            if spriteURL != None:
                spriteResponse = requests.get(spriteURL)
            if spriteShinyURL != None:
                shinySpriteResponse = requests.get(spriteShinyURL)

            if  spriteURL == None or not spriteResponse.ok:
                return render_pokedex(pokemonInfoDict=pokemonInfoDict.items())
            if  spriteShinyURL == None or not shinySpriteResponse.ok:
                return render_pokedex(pokemonInfoDict=pokemonInfoDict.items(), spriteURL=spriteURL)

            return render_pokedex(pokemonInfoDict=pokemonInfoDict.items(), spriteURL=spriteURL, spriteShinyURL=spriteShinyURL)
        
    else:
        return render_pokedex()