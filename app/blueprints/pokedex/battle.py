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

        if typeModifier > 1:
            return damage, True
        return math.floor(damage), False

    def returnScaledPokemon(self, pkmn, level, remainingHealth=False):
        pkmn.level = level
        pkmn.scaledAtk = (pkmn.baseAtk * 2 + 31) * (level / 100) + 5
        pkmn.scaledDef = (pkmn.baseDef * 2 + 31) * (level / 100) + 5
        pkmn.scaledSpAtk = (pkmn.baseSpAtk * 2 + 31) * (level / 100) + 5
        pkmn.scaledSpDef = (pkmn.baseAtk * 2 + 31) * (level / 100) + 5
        pkmn.scaledSpd = (pkmn.baseAtk * 2 + 31) * (level / 100) + 5

        if remainingHealth:
            pkmn.scaledHP = remainingHealth
        else:
            pkmn.scaledHP = (pkmn.baseHP * 2 + 31) * (level / 100) + 10 + level

        return pkmn

    def battleRunner(playerTeam, enemyTeam, battle):
        pass

    def battle(
        self,
        playerPkmn,
        enemyPkmn,
        lastRound=True,
        playerPkmnRemainingHealth=False,
        enemyPkmnRemainingHealth=False,
    ):
        def hit(move):
            hitChance = random.randint(1, 101)
            missThreshold = 100 - int(move.accuracy)

            if hitChance > missThreshold:
                return True

            return False

        pokemon1 = self.returnScaledPokemon(playerPkmn, 100, playerPkmnRemainingHealth)
        pokemon2 = self.returnScaledPokemon(enemyPkmn, 100, enemyPkmnRemainingHealth)
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
                damage, superEffective = self.calculateDamage(attacker, defender)
                defender.scaledHP -= damage
                battleLog.append(
                    f"{attacker.name} hit {defender.name} for {damage} damage!"
                )
                if superEffective:
                    battleLog.append("It's super effective!")
            else:
                battleLog.append(f"{attacker.name} missed.")

        if defender.scaledHP > attacker.scaledHP:
            winner = defender
            fainted = attacker.name

        else:
            winner = attacker
            fainted = defender.name

        battleLog.append(f"{fainted} fainted.")
        if lastRound:
            battleLog.append(f"{winner.name} wins!")

        return battleLog, winner
