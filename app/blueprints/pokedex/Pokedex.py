import requests, random
from flask import render_template, flash
from app.models import Pkmn, UnownLetters, db
from sqlalchemy import func

class Pokedex():
    def __init__(self, form=None):
        self.form = form

    def unownSpeller(self, wordToSpell=True):
        errorMessages = ['oops', 'sorry', '?', 'huh', 'nani', 'what', 'wtf']
        if wordToSpell == True:
           wordToSpell = errorMessages[random.randint(0,len(errorMessages) - 1)]
        
        unownWord = []
        for char in wordToSpell.upper():
            unownLetter = UnownLetters.query.filter(UnownLetters.symbol == char).first()

            unownWord.append(unownLetter.spriteShiny if random.randint(0,10) == 5 else unownLetter.sprite)

        return unownWord
    
    def unownErrorMessage(self, form, *args):
        unownWord = self.unownSpeller()
        
        return render_template(*args, form=form, unownWord=unownWord)

    # def returnSpriteURL(self, pkmn=10027, pkmnType="pokemon-form", shiny=False):
    #     """returns a pokemon sprite from id or name (accepts string or int)
        
    #     default returns a pokemon-form, pkmnType='pokemon' to return a regular pokemon"""
    #     url = f"https://pokeapi.co/api/v2/{pkmnType}/{pkmn}"
    #     response = requests.get(url)

    #     if not response.ok:
    #         return response.status_code
    #     else:
    #         data = response.json()
    #         return data["sprites"][f"front_{'shiny' if shiny else 'default'}"]

    # def renderSprite(self, errorCode, unownWord=False, *args):
    
    #     sprite = self.returnSpriteURL()

    #     if len(sprite) == 3:
    #         return self.render_pokedex(connectErrorCode=sprite)

    #     else:
    #         if unownWord:
    #             return self.render_pokedex(errorCode=errorCode, unownWord=self.unownSpeller(unownWord))
    #         else:
    #             return self.render_pokedex(errorCode=errorCode, sprite=sprite)

    def returnPokemonData(self, form, favorite=False, catch=False, favoriteSprite=False, shiny=False):
        def populatePkmnTableFromAPI(data):
            def unpackTuple(arr):
                if len(arr) > 1:
                    return arr[0], arr[1]
                else:
                    return arr[0], 'None'
            
            def unpackStats(data):
                hp, atk, defense, spatk, spdef, spd = [stat['base_stat'] for stat in data['stats']]

                return hp, atk, defense, spatk, spdef, spd
                
            spriteURL = data['sprites']['front_default']
            spriteShinyURL = data['sprites']['front_shiny']
            pokedexID = data['id']
            name = data['name'].title()
            abilities = [ability['ability']['name'].title() for ability in data['abilities'] if ability['is_hidden'] == False]
            baseExp = data['base_experience']
            pokemonType = [pkmnType['type']['name'].title() for pkmnType in data['types']]
            
            try:
                hiddenAbility = [ability['ability']['name'].title() for ability in data['abilities'] if ability['is_hidden'] == True][0]
            except:
                hiddenAbility = 'None'

            firstType, secondType = unpackTuple(pokemonType)
            firstAbility, secondAbility = unpackTuple(abilities)
            hp, atk, defense, spatk, spdef, spd = unpackStats(data)

            pokemon = Pkmn(pokedexID, name, spriteURL, spriteShinyURL, firstType, secondType, firstAbility, secondAbility, hiddenAbility, baseExp, hp, atk, defense, spatk, spdef, spd)
            
            try:
                db.session.add(pokemon)
                db.session.commit()
                flash(f"Successfully added {name} to DataBase!", "success")
                return pokemon
            except:
                db.session.rollback()
                flash(f"Error adding {name} to DataBase...", "error")
                return False

        def returnPokemonInfoDict(pokemon):
            pkmnInfo = [pokemon.name, pokemon.id, pokemon.firstType, pokemon.secondType, pokemon.firstAbility, pokemon.secondAbility, pokemon.hiddenAbility, pokemon.baseEXP, pokemon.baseHP, pokemon.baseAtk, pokemon.baseDef, pokemon.baseSpAtk, pokemon.baseSpDef, pokemon.baseSpd]
            labels = ["Name:", "ID:", "Type:", "Ability 1:", "Ability 2:", "Hidden Ability:", "Base Exp:", "HP:", "ATK:", "DEF:", "SPATK:", "SPDEF:", "SPD:"]
            
            pokemonInfoDict = dict(zip(labels, pkmnInfo))

            return pokemonInfoDict, pokemon.sprite, pokemon.spriteShiny

        def titlePokemon(name):
            if name.isdigit():
                return name
            else:
                splitName = name.split('-')
                return '-'.join([split.title() for split in splitName])
            
        if favoriteSprite:
            id = form
        else:
            id = titlePokemon(form.pokedexInput.data.strip().lower())

        if id.isdigit():
            identifier = Pkmn.id
        else:
            identifier = Pkmn.name

        pokemon = Pkmn.query.filter(identifier == id).first()
        
        if pokemon:
            if not favorite and not catch and not favoriteSprite:
                return returnPokemonInfoDict(pokemon)
        else:
            url = f"https://pokeapi.co/api/v2/pokemon/{id.lower()}"
            response = requests.get(url)

            if not response.ok or id.isspace():
                return response.status_code
            
            data = response.json()

            pokemon = populatePkmnTableFromAPI(data)

            if pokemon == False:
                return False

        if favorite:
            return pokemon.name, pokemon.id, pokemon.sprite, pokemon.spriteShiny
        elif catch:
            shinyChance = random.randint(0,10)
            return pokemon.name, pokemon.id, pokemon.spriteShiny if shinyChance == 5 else pokemon.sprite
        elif favoriteSprite:
            if shiny:
                return pokemon.spriteShiny
            else:
                return pokemon.sprite
        else:
            return returnPokemonInfoDict(pokemon)