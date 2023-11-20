import requests, random
from flask import render_template, flash
from app.models import (
    Pkmn,
    UnownLetters,
    db,
    PkmnMoves,
    statusMovesLearnableByPokemon,
    damageMovesLearnableByPokemon,
)
from .forms import PokedexInputForm


class Pokedex:
    def __init__(self, form=None):
        self.form = form

    def populateUnownAlphabetDB(self):
        for idx in range(0, 28):
            if idx == 0:
                mod, idx = "", 201
            else:
                idx += 10000

            url = f"https://pokeapi.co/api/v2/pokemon-form/{mod}{idx}"

            response = requests.get(url)

            if not response.ok:
                return response.status_code

            data = response.json()

            unownLetter = UnownLetters(
                data["form_names"][6]["name"],
                data["sprites"]["front_default"],
                data["sprites"]["front_shiny"],
            )
            db.session.add(unownLetter)

        db.session.commit()
        return True

    def unownSpeller(self, wordToSpell=True):
        errorMessages = ["oops", "sorry", "?", "huh", "nani", "what", "wtf"]
        if wordToSpell == True:
            wordToSpell = errorMessages[random.randint(0, len(errorMessages) - 1)]

        unownWord = []
        for char in wordToSpell.upper():
            unownLetter = UnownLetters.query.filter(UnownLetters.symbol == char).first()

            unownWord.append(
                unownLetter.spriteShiny
                if random.randint(0, 10) == 5
                else unownLetter.sprite
            )

        return unownWord

    def unownMessage(self, form, wordToSpell=True, *args):
        def delayModifier(arrLen=5, idx=False, lastRand=False):
            if idx:
                return "-top" if idx % 2 == 0 else "-bottom"
            elif wordToSpell == "welcome":
                rand = lastRand
                while rand == lastRand:
                    rand = random.randint(1, arrLen)
                return rand
            else:
                return ""

        unownWord = self.unownSpeller(wordToSpell)

        errorMessage = "Couldn't find that one..."
        htmlContent = "<div>"
        lastRand = 0
        for idx, sprite in enumerate(unownWord):
            rand = delayModifier(lastRand=lastRand)
            htmlContent += f'<img src="{sprite}" class="sprite delay-show{rand}">'
            lastRand = rand
        htmlContent += "</div>"
        if wordToSpell != "welcome":
            htmlContent += f'<div class="animated-text">{errorMessage}</div>'

        return render_template(*args, form=form, unownMessage=htmlContent)

    def titlePokemon(self, name):
        name = name.lower().strip()
        if name.isdigit():
            return name
        else:
            splitName = name.split("-")
            return "-".join([split.title() for split in splitName])

    def populateMovesDB(self, data, pkmnObj):
        def bulkAddMoves(movesToAdd):
            def getAPIData(url):
                response = requests.get(url)

                if not response.ok:  # if api call returned an error
                    return response.status_code  # return the error

                data = response.json()  # process the json

                return data

            lastMoveIdx = (
                len(movesToAdd) - 1
            )  # define the number of moves to add for flash message after successful commit
            addedMoves = []

            for idx, url in enumerate(
                movesToAdd
            ):  # for every move to be added to the db
                end = idx == lastMoveIdx
                addedMoves.append(
                    self.addMoveToDB(getAPIData(url), end, lastMoveIdx + 1)
                )  # add the move to the db and return the associated move object

            return addedMoves  # return all recently added move objects

        learnableMovesDict = {}  # create empty dict to hold move name and api url
        for move in data["moves"]:  # for every name/url pair
            learnableMovesDict[move["move"]["name"].lower()] = move["move"][
                "url"
            ]  # populate the dict with move name as key and move api url as value

        learnableMoveObjs = []
        for move in db.session.query(
            PkmnMoves
        ).all():  # for every move currently inside the database
            currentMove = move.name.lower()
            if currentMove in list(
                learnableMovesDict.keys()
            ):  # if that move is in the dict of moves this pokemon can learn
                learnableMoveObjs.append(move)  # add that move object to the list
                del learnableMovesDict[
                    currentMove
                ]  # delete the name/url pair from the dict

        try:
            addedMoveObjs = bulkAddMoves(
                list(learnableMovesDict.values())
            )  # add all of the moves that are learnable by this pokemon that aren't current in the db
        except Exception as e:
            flash(f"{e}", "error")

        learnableMoveObjs += addedMoveObjs  # combine the list of moves that were in the db with moves that were added to the db

        damageValues = []
        statusValues = []
        for (
            moveObj
        ) in learnableMoveObjs:  # for every move object this pokemon can learn
            if moveObj.power == "none":
                statusValues.append({"pkmn_id": pkmnObj.id, "move_id": moveObj.id})
            else:
                damageValues.append({"pkmn_id": pkmnObj.id, "move_id": moveObj.id})

        try:
            statusAssociation = statusMovesLearnableByPokemon.insert().values(
                statusValues
            )
            db.session.execute(statusAssociation)

            damageAssociation = damageMovesLearnableByPokemon.insert().values(
                damageValues
            )
            db.session.execute(damageAssociation)

            db.session.commit()
            flash("Association created successfully!", "success")

            return True
        except:
            flash("Error creating association...", "error")
            return False

    def addMoveToDB(self, data, lastMoveToAdd=True, totalMovesToAdd=1):
        def findEnglishText(data, key, endpoint):
            entry = checkNull(data, key)
            if entry == None:
                pass
            else:
                for text in entry:
                    if checkNull(text, "language", "name") == "en":
                        return text[endpoint]
            return "none"

        def checkNull(data, *args):
            for key in args:
                data = data.get(key)
                if data == None:
                    return "none"

            return data

        move = PkmnMoves(
            checkNull(data, "id"),
            moveName := checkNull(data, "name"),
            checkNull(data, "meta", "category", "name"),
            checkNull(data, "power"),
            checkNull(data, "meta", "min_hits"),
            checkNull(data, "meta", "max_hits"),
            checkNull(data, "meta", "ailment", "name"),
            checkNull(data, "meta", "ailment_chance"),
            checkNull(data, "type", "name"),
            checkNull(data, "meta", "crit_rate"),
            checkNull(data, "meta", "drain"),
            checkNull(data, "meta", "flinch_chance"),
            checkNull(data, "meta", "healing"),
            checkNull(data, "meta", "max_turns"),
            checkNull(data, "meta", "min_turns"),
            checkNull(data, "meta", "stat_chance"),
            checkNull(data, "damage_class", "name"),
            checkNull(data, "accuracy"),
            checkNull(data, "effect_chance"),
            checkNull(data, "priority"),
            checkNull(data, "pp"),
            checkNull(data, "target", "name"),
            findEnglishText(data, "effect_entries", "effect"),
            findEnglishText(data, "flavor_text_entries", "flavor_text"),
        )
        db.session.add(move)

        if lastMoveToAdd:
            flash(
                f"Successfully added {moveName if totalMovesToAdd == 1 else str(totalMovesToAdd) + ' moves'} to DataBase",
                "success",
            )
        return move

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
                    data.category,
                    data.power,
                    data.minHits,
                    data.maxHits,
                    data.ailment,
                    data.ailmentChance,
                    data.moveType,
                    data.critRate,
                    data.drain,
                    data.flinchChance,
                    data.healing,
                    data.maxTurns,
                    data.minTurns,
                    data.statChance,
                    data.damageClass,
                    data.accuracy,
                    data.effectChance,
                    data.priority,
                    data.pp,
                    data.target,
                    data.effect,
                    data.flavorText,
                ]

            labels = [
                "ID",
                "Name",
                "Category",
                "Power",
                "Min Hits",
                "Max Hits",
                "Ailment",
                "Ailment Chance",
                "Move Type",
                "Crit Rate",
                "Drain",
                "Flinch Chance",
                "Healing",
                "Max Turns",
                "Min Turns",
                "Stat Chance",
                "Damage Class",
                "Accuracy",
                "Effect Chance",
                "Priority",
                "PP",
                "Target",
                "Effect",
                "Flavor Text",
            ]

            if isinstance(data, PkmnMoves):
                moveInfo = fromDB(data)
            else:
                moveInfo = fromAPI(data)

            if moveInfo:
                return dict(zip(labels, moveInfo))
            else:
                return False

        moveToCheck = form.pokedexInput.data.strip().lower()  # get user input from form

        if moveToCheck.isdigit():  # if an id was entered
            identifier = PkmnMoves.id
        else:  # if a name was entered
            identifier = PkmnMoves.name

        # check if user input exists in db
        validMove = PkmnMoves.query.filter(identifier == moveToCheck).first()

        if validMove:  # if user input exists in db
            return createMoveDict(validMove)  # return dict
        else:  # if user input does not exist in db
            url = f"https://pokeapi.co/api/v2/move/{moveToCheck}/"  # generate api url
            response = requests.get(url)

            if not response.ok:  # if api call returned an error
                return response.status_code  # return the error

            data = response.json()  # process the json
            return createMoveDict(
                data
            )  # process the json and add to db, then return dict

    def randomShinyChance(self, pkmnObj):
        shinyChance = random.randint(1, 10)

        shiny = True if shinyChance == 5 and pkmnObj.spriteShiny != None else False
        pkmnObj.shiny = shiny

        pkmnObj.spriteShiny
        pkmnObj.chosenSprite = pkmnObj.spriteShiny if shiny else pkmnObj.sprite

        pkmnObj.chosenSprite = pkmnObj.sprite
        return pkmnObj

    def returnPokemonObj(self, form):
        def populatePkmnTableFromAPI(data):
            def unpackTuple(arr):
                if len(arr) > 1:
                    return arr[0], arr[1]
                else:
                    return arr[0], "None"

            def unpackStats(data):
                hp, atk, defense, spatk, spdef, spd = [
                    stat["base_stat"] for stat in data["stats"]
                ]

                return hp, atk, defense, spatk, spdef, spd

            spriteURL = data["sprites"]["front_default"]
            spriteShinyURL = data["sprites"]["front_shiny"]
            spriteBackURL = data["sprites"]["back_default"]
            spriteShinyBackURL = data["sprites"]["front_shiny"]
            pokedexID = data["id"]
            name = data["name"].title()
            abilities = [
                ability["ability"]["name"].title()
                for ability in data["abilities"]
                if ability["is_hidden"] == False
            ]
            baseExp = data["base_experience"]
            pokemonType = [
                pkmnType["type"]["name"].title() for pkmnType in data["types"]
            ]

            try:
                hiddenAbility = [
                    ability["ability"]["name"].title()
                    for ability in data["abilities"]
                    if ability["is_hidden"] == True
                ][0]
            except:
                hiddenAbility = "None"

            firstType, secondType = unpackTuple(pokemonType)
            firstAbility, secondAbility = unpackTuple(abilities)
            hp, atk, defense, spatk, spdef, spd = unpackStats(data)

            pokemon = Pkmn(
                pokedexID,
                name,
                spriteURL,
                spriteShinyURL,
                spriteBackURL,
                spriteShinyBackURL,
                firstType,
                secondType,
                firstAbility,
                secondAbility,
                hiddenAbility,
                baseExp,
                hp,
                atk,
                defense,
                spatk,
                spdef,
                spd,
            )

            try:
                db.session.add(pokemon)
                db.session.commit()
                flash(f"Successfully added {name} to DataBase!", "success")

                # populate moves db with moves learnable by this pokemon and create relationship between pokemon and its learnable moves
                if not self.populateMovesDB(data, pokemon):
                    return False
                return pokemon
            except:
                db.session.rollback()
                flash(f"Error adding {name} to DataBase...", "error")
                return False

        if isinstance(form, PokedexInputForm):
            id = form.pokedexInput.data
        else:
            id = form

        if isinstance(id, int) or id.isdigit():
            id = str(id)
            identifier = Pkmn.id
        else:
            id = self.titlePokemon(id)
            identifier = Pkmn.name

        pokemon = Pkmn.query.filter(identifier == id).first()
        if pokemon:
            return pokemon
        else:
            url = f"https://pokeapi.co/api/v2/pokemon/{id.lower()}"

            response = requests.get(url)

            if not response.ok or id.isspace():
                return response.status_code

            data = response.json()

            pokemon = populatePkmnTableFromAPI(data)

            if pokemon == False:
                return False

            return pokemon

    def returnPokemonSprite(self, form, shiny=False, both=False):
        pokemon = self.returnPokemonObj(form)

        if shiny:
            return pokemon.spriteShiny
        elif both:
            return (pokemon.sprite, pokemon.spriteShiny)
        else:
            return pokemon.sprite

    def returnPokemonInfoDict(self, form):
        pokemon = self.returnPokemonObj(form)

        if isinstance(pokemon, int):
            return pokemon

        pkmnInfo = [
            pokemon.name,
            pokemon.id,
            pokemon.firstType,
            pokemon.secondType,
            pokemon.firstAbility,
            pokemon.secondAbility,
            pokemon.hiddenAbility,
            pokemon.baseEXP,
            pokemon.baseHP,
            pokemon.baseAtk,
            pokemon.baseDef,
            pokemon.baseSpAtk,
            pokemon.baseSpDef,
            pokemon.baseSpd,
        ]
        labels = [
            "Name:",
            "ID:",
            "Type 1:",
            "Type 2:",
            "Ability 1:",
            "Ability 2:",
            "Hidden Ability:",
            "Base Exp:",
            "HP:",
            "ATK:",
            "DEF:",
            "SPATK:",
            "SPDEF:",
            "SPD:",
        ]

        pokemonInfoDict = dict(zip(labels, pkmnInfo))

        return pokemonInfoDict, pokemon.sprite, pokemon.spriteShiny

    # def returnPokemonData(self, form, favorite=False, catch=False, favoriteSprite=False, shiny=False, team=False, grass=False):
    #     def populatePkmnTableFromAPI(data):
    #         def unpackTuple(arr):
    #             if len(arr) > 1:
    #                 return arr[0], arr[1]
    #             else:
    #                 return arr[0], 'None'

    #         def unpackStats(data):
    #             hp, atk, defense, spatk, spdef, spd = [stat['base_stat'] for stat in data['stats']]

    #             return hp, atk, defense, spatk, spdef, spd

    #         spriteURL = data['sprites']['front_default']
    #         spriteShinyURL = data['sprites']['front_shiny']
    #         pokedexID = data['id']
    #         name = data['name'].title()
    #         abilities = [ability['ability']['name'].title() for ability in data['abilities'] if ability['is_hidden'] == False]
    #         baseExp = data['base_experience']
    #         pokemonType = [pkmnType['type']['name'].title() for pkmnType in data['types']]

    #         try:
    #             hiddenAbility = [ability['ability']['name'].title() for ability in data['abilities'] if ability['is_hidden'] == True][0]
    #         except:
    #             hiddenAbility = 'None'

    #         firstType, secondType = unpackTuple(pokemonType)
    #         firstAbility, secondAbility = unpackTuple(abilities)
    #         hp, atk, defense, spatk, spdef, spd = unpackStats(data)

    #         pokemon = Pkmn(pokedexID, name, spriteURL, spriteShinyURL, firstType, secondType, firstAbility, secondAbility, hiddenAbility, baseExp, hp, atk, defense, spatk, spdef, spd)

    #         try:
    #             db.session.add(pokemon)
    #             db.session.commit()
    #             flash(f"Successfully added {name} to DataBase!", "success")

    #             # populate moves db with moves learnable by this pokemon and create relationship between pokemon and its learnable moves
    #             if not self.populateMovesDB(data, pokemon):
    #                 return False
    #             return pokemon
    #         except:
    #             db.session.rollback()
    #             flash(f"Error adding {name} to DataBase...", "error")
    #             return False

    #     def returnPokemonInfoDict(pokemon):
    #         pkmnInfo = [pokemon.name, pokemon.id, pokemon.firstType, pokemon.secondType, pokemon.firstAbility, pokemon.secondAbility, pokemon.hiddenAbility, pokemon.baseEXP, pokemon.baseHP, pokemon.baseAtk, pokemon.baseDef, pokemon.baseSpAtk, pokemon.baseSpDef, pokemon.baseSpd]
    #         labels = ["Name:", "ID:", "Type 1:", "Type 2:", "Ability 1:", "Ability 2:", "Hidden Ability:", "Base Exp:", "HP:", "ATK:", "DEF:", "SPATK:", "SPDEF:", "SPD:"]

    #         pokemonInfoDict = dict(zip(labels, pkmnInfo))

    #         return pokemonInfoDict, pokemon.sprite, pokemon.spriteShiny

    #     if favoriteSprite or team or grass:
    #         id = str(form)
    #     else:
    #         id = self.titlePokemon(form.pokedexInput.data)

    #     if id.isdigit():
    #         identifier = Pkmn.id
    #     else:
    #         identifier = Pkmn.name

    #     pokemon = Pkmn.query.filter(identifier == id).first()

    #     if pokemon:
    #         if not favorite and not catch and not favoriteSprite and not team:
    #             return returnPokemonInfoDict(pokemon)
    #     else:
    #         url = f"https://pokeapi.co/api/v2/pokemon/{id.lower()}"
    #         response = requests.get(url)

    #         if not response.ok or id.isspace():
    #             return response.status_code

    #         data = response.json()

    #         pokemon = populatePkmnTableFromAPI(data)

    #         if pokemon == False:
    #             return False

    #     if favorite:
    #         return pokemon.name, pokemon.id, pokemon.sprite, pokemon.spriteShiny
    #     elif catch:
    #         shinyChance = random.randint(1,10)
    #         return pokemon.name, pokemon.id, pokemon.spriteShiny if shinyChance == 5 and pokemon.spriteShiny != None else pokemon.sprite, True if shinyChance == 5 and pokemon.spriteShiny != None else False
    #     elif favoriteSprite or team:
    #         if shiny:
    #             return pokemon.spriteShiny
    #         else:
    #             return pokemon.sprite
    #     elif grass:
    #         shinyChance = random.randint(1,10)
    #         shiny = True if shinyChance == 5 and pokemon.spriteShiny != None else False
    #         pokemon.shiny = shiny
    #         pokemon.chosenSprite = pokemon.spriteShiny if shiny else pokemon.sprite
    #         try:
    #             pkmnID = pokemon.id
    #         except Exception as e:
    #             breakpoint()

    #         return pokemon
    #     else:
    #         return returnPokemonInfoDict(pokemon)
