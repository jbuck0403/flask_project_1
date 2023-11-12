import requests, random
from flask import render_template

class Pokedex():
    def __init__(self, form=None):
        self.form = form

    def render_pokedex(self, **kwargs):
        self.form.pokedexInput.data = ""
        return render_template('pokedex.jinja', form=self.form, **kwargs)

    def unownSpeller(self, wordToSpell=True):
        errorMessages = ['oops', 'sorry', '?', 'huh', 'nani', 'what', 'wtf']
        if wordToSpell == True:
           wordToSpell = errorMessages[random.randint(0,len(errorMessages) - 1)]

        if wordToSpell == '?':
            unownIndexes = [10027]
        else:
            unownIndexes = [(ord(char) - 97) + 10000 if char != 'a' else 201 for char in wordToSpell.lower()]
        
        return [self.returnSpriteURL(pkmn=index, pkmnType="pokemon-form") for index in unownIndexes]
        
    def returnSpriteURL(self, pkmn=10027, pkmnType="pokemon-form", shiny=False):
        """returns a pokemon sprite from id or name (accepts string or int)
        
        default returns a pokemon-form, pkmnType='pokemon' to return a regular pokemon"""
        url = f"https://pokeapi.co/api/v2/{pkmnType}/{pkmn}"
        response = requests.get(url)

        if not response.ok:
            return response.status_code
        else:
            data = response.json()
            return data["sprites"][f"front_{'shiny' if shiny else 'default'}"]

    def renderSprite(self, errorCode, unownWord=False, *args):
    
        sprite = self.returnSpriteURL()

        if len(sprite) == 3:
            return self.render_pokedex(connectErrorCode=sprite)

        else:
            if unownWord:
                return self.render_pokedex(errorCode=errorCode, unownWord=self.unownSpeller(unownWord))
            else:
                return self.render_pokedex(errorCode=errorCode, sprite=sprite)

    def returnPokemonData(self, form, favorite=False):
        id = form.pokedexInput.data.strip()
        print(id)

        url = f"https://pokeapi.co/api/v2/pokemon/{id}"
        response = requests.get(url)

        if not response.ok or id.isspace():
            return response.status_code
        
        data = response.json()

        spriteURL = data['sprites']['front_default']
        spriteShinyURL = data['sprites']['front_shiny']
        pokedexID = data['id']
        name = data['name'].title()

        if favorite:
            return name, pokedexID, spriteURL, spriteShinyURL
        
        abilities = [ability['ability']['name'].title() for ability in data['abilities'] if ability['is_hidden'] == False]
        try:
            hiddenAbility = [ability['ability']['name'].title() for ability in data['abilities'] if ability['is_hidden'] == True][0]
        except:
            hiddenAbility = 'None'

        baseExp = data['base_experience']
        baseStats = {stat['stat']['name'].upper() + ':': stat['base_stat'] for stat in data['stats']}
        pokemonType = [pkmnType['type']['name'].title() for pkmnType in data['types']]

        pokemonType = f"{pokemonType[0]}{'/' + pokemonType[1] if len(pokemonType) > 1 else ''}"

        labels = ["Name:", "ID:", "Type:", "Ability 1:", "Ability 2:", "Hidden Ability:", "Base Exp:"] + list(baseStats.keys())
        pkmnInfo = [name, pokedexID, pokemonType, abilities[0], abilities[1] if len(abilities) > 1 else 'None', hiddenAbility, baseExp] + list(baseStats.values())
        pokemonInfoDict = dict(zip(labels, pkmnInfo))

        return pokemonInfoDict, spriteURL, spriteShinyURL