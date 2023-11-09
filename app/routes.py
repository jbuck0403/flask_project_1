from flask import request, render_template, redirect
import requests, random
from app import app
from app.forms import PokedexInputForm, LoginForm, SignupForm
from app.users import REGISTERED_USERS

@app.route("/", methods=['GET', 'POST'])
def landingPage():
    if request.method == "POST":
        return redirect("/pokedex")
    else:
        return render_template('landingPage.jinja')

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(REGISTERED_USERS.keys())

    if request.method == "POST":
        if "loginBtn" in request.form and form.validate_on_submit():
            return "Successfully logged in!"
        elif "signupBtn" in request.form:
            return redirect("/signup")
        
    else:
        return render_template('login.jinja', form=form)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if request.method == "POST" and form.validate_on_submit():
        REGISTERED_USERS[form.userName.data] = form.password
        return redirect('/login')
    else:
        return render_template('signup.jinja', form=form)


@app.route("/pokedex", methods=['GET', 'POST'])
def pokedex():
    def render_pokedex(**kwargs):
        form.pokedexInput.data = ""
        return render_template('pokedex.jinja', form=form, bulbaURL=bulbaURL, **kwargs)

    def unownSpeller(wordToSpell="oops"):
        errorMessages = ['oops', 'sorry', '?', 'huh', 'nani']
        if wordToSpell == True:
           wordToSpell = errorMessages[random.randint(0,len(errorMessages) - 1)]
        
        if wordToSpell == '?':
            unownIndexes = [10027]
        else:
            unownIndexes = [(ord(char) - 97) + 10000 if char != 'a' else 201 for char in wordToSpell.lower()]
        
        return [returnSpriteURL(pkmn=index, pkmnType="pokemon-form") for index in unownIndexes]
        
    def returnSpriteURL(pkmn=10027, pkmnType="pokemon-form", shiny=False):
        url = f"https://pokeapi.co/api/v2/{pkmnType}/{pkmn}"
        response = requests.get(url)

        if not response.ok:
            return response.status_code
        else:
            data = response.json()
            return data["sprites"][f"front_{'shiny' if shiny else 'default'}"]

    def renderSprite(errorCode, unownWord=False):
        sprite = returnSpriteURL()

        if len(sprite) == 3:
            return render_pokedex(connectErrorCode=sprite)

        else:
            if unownWord:
                return render_pokedex(errorCode=errorCode, unownWord=unownSpeller(unownWord))
            else:
                return render_pokedex(errorCode=errorCode, sprite=sprite)

    def returnPokemonData():
        id = form.pokedexInput.data

        url = f"https://pokeapi.co/api/v2/pokemon/{id}"
        response = requests.get(url)

        if not response.ok:
            return renderSprite, response.status_code 
            
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

        return pokemonInfoDict, spriteURL, spriteShinyURL


    form = PokedexInputForm()
    bulbaURL = None

    if request.method == "POST" and form.validate_on_submit():

        pokemonData = returnPokemonData()

        if (callable(pokemonData[0])):
            return pokemonData[0](pokemonData[1], unownWord=True)
        else:
            pokemonInfoDict, spriteURL, spriteShinyURL = pokemonData

        bulbaURL = f"https://bulbapedia.bulbagarden.net/wiki/{pokemonInfoDict['Name:']}_(Pok%C3%A9mon)"

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