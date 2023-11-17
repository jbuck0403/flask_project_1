import requests, random
from flask import render_template, flash
from app.models import Pkmn, UnownLetters, db, PkmnMoves
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
    
    def unownMessage(self, form, wordToSpell=True, *args):
        def delayModifier(arrLen = 5, idx=False, lastRand=False):
            if idx:
                return "-top" if idx % 2 == 0 else "-bottom"
            elif wordToSpell == 'welcome':
                rand = lastRand
                while rand == lastRand:
                    rand = random.randint(1,arrLen)
                return rand
            else:
                return ''

        unownWord = self.unownSpeller(wordToSpell)

        errorMessage = "Couldn't find that one..."
        htmlContent = '<div>'
        lastRand = 0
        for idx, sprite in enumerate(unownWord):
            rand = delayModifier(lastRand=lastRand)
            htmlContent += f'<img src="{sprite}" class="sprite delay-show{rand}">'
            lastRand = rand
        htmlContent += '</div>'
        if wordToSpell != 'welcome':
            htmlContent += f'<div class="animated-text">{errorMessage}</div>'

        return render_template(*args, form=form, unownMessage=htmlContent)

    def titlePokemon(self, name):
            name = name.lower().strip()
            if name.isdigit():
                return name
            else:
                splitName = name.split('-')
                return '-'.join([split.title() for split in splitName])

    def addMoveToDB(self, data):
        move = PkmnMoves(
                        data['id'],
                        moveName := self.titlePokemon(data['name']),
                        data['power'],
                        data['type']['name'].title(),
                        data['damage_class']['name'].title(),
                        data['accuracy'],
                        data['priority'],
                        data['pp'],
                        data['flavor_text_entries'][0]['flavor_text']
                    )
        try:
            db.session.add(move)
            db.session.commit()
            flash(f"Successfully added {moveName} to DataBase", "success")
            return move
        except:
            db.session.rollback()
            flash(f"Error adding {moveName} to DataBase", "error")
            return False

    def returnPokemonMove(self, form):
        def createMoveDict(data):
            def fromAPI(data):
                if move := self.addMoveToDB(data):
                    return fromDB(move)
                else:
                    return False

            def fromDB(data):
                return [
                        data.id,
                        data.name,
                        data.power,
                        data.type,
                        data.damageClass,
                        data.accuracy,
                        data.priority,
                        data.pp,
                        data.flavorText
                    ]

            labels = ["ID",'Name','Power','Type','Damage Class','Accuracy','Priority','PP','Flavor Text']
            
            if isinstance(data, PkmnMoves):
                moveInfo = fromDB(data)
            else:
                moveInfo = fromAPI(data)
            
            if moveInfo:
                return dict(zip(labels, moveInfo))
            else: return False

        moveToCheck = form.pokedexInput.data.strip().lower() # get user input from form
        
        if moveToCheck.isdigit(): # if an id was entered
            identifier = PkmnMoves.id
        else: # if a name was entered
            identifier = PkmnMoves.name

        # check if user input exists in db
        validMove= PkmnMoves.query.filter(identifier == moveToCheck).first()
        
        if validMove: # if user input exists in db
            return createMoveDict(validMove) # return dict
        else: # if user input does not exist in db
            url = f"https://pokeapi.co/api/v2/move/{moveToCheck}/" # generate api url
            response = requests.get(url)

            if not response.ok: # if api call returned an error
                return response.status_code # return the error
            
            data = response.json() # process the json
            return createMoveDict(data) # process the json and add to db, then return dict

    def returnPokemonData(self, form, favorite=False, catch=False, favoriteSprite=False, shiny=False, team=False):
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
            labels = ["Name:", "ID:", "Type 1:", "Type 2:", "Ability 1:", "Ability 2:", "Hidden Ability:", "Base Exp:", "HP:", "ATK:", "DEF:", "SPATK:", "SPDEF:", "SPD:"]
            
            pokemonInfoDict = dict(zip(labels, pkmnInfo))

            return pokemonInfoDict, pokemon.sprite, pokemon.spriteShiny
            
        if favoriteSprite or team:
            id = str(form)
        else:
            id = self.titlePokemon(form.pokedexInput.data)

        if id.isdigit():
            identifier = Pkmn.id
        else:
            identifier = Pkmn.name

        pokemon = Pkmn.query.filter(identifier == id).first()
        
        if pokemon:
            if not favorite and not catch and not favoriteSprite and not team:
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
            shinyChance = random.randint(1,10)
            return pokemon.name, pokemon.id, pokemon.spriteShiny if shinyChance == 5 and pokemon.spriteShiny != None else pokemon.sprite, True if shinyChance == 5 and pokemon.spriteShiny != None else False
        elif favoriteSprite or team:
            if shiny:
                return pokemon.spriteShiny
            else:
                return pokemon.sprite
        else:
            return returnPokemonInfoDict(pokemon)