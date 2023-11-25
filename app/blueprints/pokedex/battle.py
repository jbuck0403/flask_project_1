import copy, random, math
from app.models import (
    db,
    Battle,
    Turn,
    TurnDescription,
    Pkmn,
    PkmnMoves,
    PkmnTeam,
    User,
)
from flask_login import current_user
from flask import session
from sqlalchemy import func


class PokemonBattle:
    WEAKNESSCHART = {
        "bug": {
            "weak": ["fire", "flying", "rock"],
            "strong": ["dark", "grass", "psychic"],
        },
        "dark": {"weak": ["bug", "fairy", "fighting"], "strong": ["ghost", "psychic"]},
        "dragon": {"weak": ["dragon", "ice", "fairy"], "strong": ["dragon"]},
        "electric": {"weak": ["ground"], "strong": ["water", "flying"]},
        "fairy": {
            "weak": ["poison", "steel"],
            "strong": ["dark", "dragon", "fighting"],
        },
        "fighting": {
            "weak": ["fairy", "flying", "psychic"],
            "strong": ["dark", "ice", "normal", "rock", "steel"],
        },
        "fire": {
            "weak": ["water", "rock", "ground"],
            "strong": ["bug", "grass", "ice", "steel"],
        },
        "flying": {
            "weak": ["electric", "ice", "rock"],
            "strong": ["bug", "fighting", "grass"],
        },
        "ghost": {"weak": ["dark", "ghost"], "strong": ["psychic", "ghost"]},
        "grass": {
            "weak": ["fire", "ice", "poison", "flying", "bug"],
            "strong": ["ground", "rock", "water"],
        },
        "ground": {
            "weak": ["grass", "ice", "water"],
            "strong": ["electric", "poison", "rock", "steel"],
        },
        "ice": {
            "weak": ["fire", "fighting", "rock", "steel"],
            "strong": ["dragon", "flying", "grass", "ground"],
        },
        "normal": {"weak": ["fighting"], "strong": []},
        "poison": {"weak": ["ground", "psychic"], "strong": ["fairy", "grass"]},
        "psychic": {"weak": ["bug", "dark", "ghost"], "strong": ["fighting", "poison"]},
        "rock": {
            "weak": ["fighting", "grass", "ground", "steel", "water"],
            "strong": ["bug", "fire", "flying", "ice"],
        },
        "steel": {
            "weak": ["fighting", "fire", "ground"],
            "strong": ["fairy", "ice", "rock"],
        },
        "water": {"weak": ["electric", "grass"], "strong": ["fire", "ground", "rock"]},
    }

    def calculateDamage(self, attacker, defender):
        """accepts Pkmn and PkmnMove objects"""

        def calculateAttack():
            if attacker.move.damageClass == "physical":
                return attacker.scaledAtk
            else:
                return attacker.scaledSpAtk

        def calculateDefense():
            if attacker.move.damageClass == "physical":
                return defender.scaledDef
            else:
                return defender.scaledSpDef

        def calculateStab():
            multiplier = 1
            if (
                attacker.move.moveType == attacker.firstType
                or attacker.move.moveType == attacker.secondType
            ):
                multiplier == 1.5

            return multiplier

        def calculateStrengthWeakness():
            multiplier = 1
            defenderWeakAgainst = self.WEAKNESSCHART[attacker.move.moveType]["weak"]
            defenderStrongAgainst = self.WEAKNESSCHART[attacker.move.moveType]["strong"]
            if attacker.firstType in defenderWeakAgainst:
                multiplier *= 2
            elif attacker.firstType in defenderStrongAgainst:
                multiplier *= 0.5

            if attacker.secondType in defenderWeakAgainst:
                multiplier *= 2
            elif attacker.secondType in defenderStrongAgainst:
                multiplier *= 1.5

            return multiplier

        attack = calculateAttack()
        defense = calculateDefense()
        stabModifier = calculateStab()
        typeModifier = calculateStrengthWeakness()

        damage = (
            (
                (
                    (
                        (((2 * int(attacker.level)) / 5) + 2)
                        * int(attacker.move.power)
                        * (attack / defense)
                    )
                    / 50
                )
                + 2
            )
            * stabModifier
            * typeModifier
        )

        crit = random.randint(0, 10001)
        if crit <= 417:
            damage *= 2
            crit = True
        else:
            crit = False

        if typeModifier > 1:
            return damage, True, crit
        return math.floor(damage), False, crit

    def returnScaledPokemon(self, pkmn, level, remainingHealth=False, team=False):
        if team:
            pkmn = pkmn.pkmn

        pkmn.level = level
        pkmn.scaledAtk = (pkmn.baseAtk * 2 + 31) * (level / 100) + 5
        pkmn.scaledDef = (pkmn.baseDef * 2 + 31) * (level / 100) + 5
        pkmn.scaledSpAtk = (pkmn.baseSpAtk * 2 + 31) * (level / 100) + 5
        pkmn.scaledSpDef = (pkmn.baseSpDef * 2 + 31) * (level / 100) + 5
        pkmn.scaledSpd = (pkmn.baseSpd * 2 + 31) * (level / 100) + 5

        if remainingHealth:
            pkmn.scaledHP = remainingHealth
        else:
            pkmn.scaledHP = (pkmn.baseHP * 2 + 31) * (level / 100) + 10 + level

        return pkmn

    def checkWinner(self, playerTeam, enemyTeam, turn):
        print("ENTERED CHECKWINNER")
        if turn.playerPkmnHP <= 0:
            if playerTeam[-1].pkmnID == turn.playerPkmnID:
                enemyUserName = (
                    db.session.query(User)
                    .filter(User.id == enemyTeam[0].trainerID)
                    .first()
                    .userName
                )
                session["winnerMessage"] = f"You were defeated by {enemyUserName}..."
                # breakpoint()
                print("WINNER", enemyTeam[0].trainerID)
                return True

        elif turn.enemyPkmnHP <= 0:
            if enemyTeam[-1].pkmnID == turn.enemyPkmnID:
                enemyUserName = (
                    db.session.query(User)
                    .filter(User.id == enemyTeam[0].trainerID)
                    .first()
                    .userName
                )
                session["winnerMessage"] = f"You won against {enemyUserName}!"
                print("WINNER", playerTeam[0].trainerID)
                # breakpoint()
                return True

        return False

    def teamBattle(self, playerTeam, enemyTeam, battleID, firstTurn):
        battleLog = []

        if firstTurn == 1:
            playerPkmn = playerTeam[0]
            enemyPkmn = enemyTeam[0]

            battleLog = self.duel(playerPkmn, enemyPkmn, battleID)

        else:
            lastTurn = (
                db.session.query(Turn)
                .filter(Turn.battleID == battleID)
                .order_by(Turn.id.desc())
                .first()
            )

            pokemonSet = False

            for idx, playerPokemon in enumerate(playerTeam):
                if playerPokemon.pkmnID == lastTurn.playerPkmnID:
                    if lastTurn.playerPkmnHP <= 0:
                        playerPkmn = playerTeam[idx + 1]
                        for pokemon in enemyTeam:
                            if pokemon.pkmnID == lastTurn.enemyPkmnID:
                                enemyPkmn = pokemon
                                pokemonSet = True

                                session["playerPkmnID"] = playerPkmn.pkmnID
                                session["enemyPkmnID"] = enemyPkmn.pkmnID
                                battleLog = self.duel(
                                    playerPkmn,
                                    enemyPkmn,
                                    battleID,
                                    enemyPkmnRemainingHealth=lastTurn.enemyPkmnHP,
                                )
                                # breakpoint()
                                break

            if not pokemonSet:
                for idx, enemyPokemon in enumerate(enemyTeam):
                    if enemyPokemon.pkmnID == lastTurn.enemyPkmnID:
                        if lastTurn.enemyPkmnHP <= 0:
                            enemyPkmn = enemyTeam[idx + 1]
                            for pokemon in playerTeam:
                                if pokemon.pkmnID == lastTurn.playerPkmnID:
                                    playerPkmn = pokemon

                                    session["playerPkmnID"] = playerPkmn.pkmnID
                                    session["enemyPkmnID"] = enemyPkmn.pkmnID
                                    battleLog = self.duel(
                                        playerPkmn,
                                        enemyPkmn,
                                        battleID,
                                        playerPkmnRemainingHealth=lastTurn.playerPkmnHP,
                                    )
                                    # breakpoint()
                                    break

        currentTurn = (
            db.session.query(Turn)
            .filter(Turn.battleID == battleID)
            .order_by(Turn.id.desc())
            .first()
        )
        self.checkWinner(playerTeam, enemyTeam, currentTurn)
        # breakpoint()
        return battleLog

    def duel(
        self,
        playerPkmn,
        enemyPkmn,
        battleID=False,
        playerPkmnRemainingHealth=False,
        enemyPkmnRemainingHealth=False,
        level=100,
    ):
        """have 2 pokemon fight until one faints"""

        def hit(move):
            hitChance = random.randint(1, 101)
            missThreshold = 100 - int(move.accuracy)

            if hitChance > missThreshold:
                return True

            return False

        pokemon1 = self.returnScaledPokemon(
            playerPkmn, level, playerPkmnRemainingHealth, battleID
        )
        pokemon2 = self.returnScaledPokemon(
            enemyPkmn, level, enemyPkmnRemainingHealth, battleID
        )

        pokemon1.move = playerPkmn.move
        pokemon2.move = enemyPkmn.move

        battleLog = []

        firstRound = True
        while pokemon1.scaledHP > 0 and pokemon2.scaledHP > 0:
            if firstRound:
                if pokemon1.scaledSpd > pokemon2.scaledSpd:
                    attacker = pokemon1
                    defender = pokemon2
                else:
                    attacker = pokemon2
                    defender = pokemon1

                firstRound = False
            else:
                attacker, defender = defender, attacker

            battleLog.append(f"{attacker.name} used {attacker.move.name}")
            if hit(attacker.move):
                damage, superEffective, crit = self.calculateDamage(attacker, defender)
                defender.scaledHP -= damage
                battleLog.append(
                    f"{attacker.name} hit {defender.name} for {damage} damage!"
                )
                if superEffective:
                    battleLog.append("It's super effective!")
                if crit:
                    battleLog.append("Critical hit!")
            else:
                battleLog.append(f"{attacker.name} missed.")

        if defender.scaledHP > attacker.scaledHP:
            winner = defender
            fainted = attacker.name

        else:
            winner = attacker
            fainted = defender.name

        battleLog.append(f"{fainted} fainted.")
        if not battleID:
            battleLog.append(f"{winner.name} wins!")

        battleLog = "/".join(battleLog)

        if battleID:
            currentTurn = Turn(
                battleID,
                pokemon1.id,
                pokemon1.scaledHP,
                pokemon2.id,
                pokemon2.scaledHP,
                battleLog,
            )
            db.session.add(currentTurn)
            db.session.commit()
            print("!!!!!!!!!!!!!!!", currentTurn.id)

        return battleLog
