import copy

class pokemonBattle():
    WEAKNESSCHART = {
        "bug": {
            "weak": ["fire", "flying", "rock"],
            "strong": ["dark", "grass", "psychic"]
        },
        "dark": {
            "weak": ["bug", "fairy", "fighting"],
            "strong": ["ghost", "psychic"]
        },
        "dragon": {
            "weak": ["dragon", "ice", "fairy"],
            "strong": ["dragon"]
        },
        "electric": {
            "weak": ["ground"],
            "strong": ["water", "flying"]
        },
        "fairy": {
            "weak": ["poison", "steel"],
            "strong": ["dark", "dragon", "fighting"]
        },
        "fighting": {
            "weak": ["fairy", "flying", "psychic"],
            "strong": ["dark", "ice", "normal", "rock", "steel"]
        },
        "fire": {
            "weak": ["water", "rock", "ground"],
            "strong": ["bug", "grass", "ice", "steel"]
        },
        "flying": {
            "weak": ["electric", "ice", "rock"],
            "strong": ["bug", "fighting", "grass"]
        },
        "ghost": {
            "weak": ["dark", "ghost"],
            "strong": ["psychic", "ghost"]
        },
        "grass": {
            "weak": ["fire", "ice", "poison", "flying", "bug"],
            "strong": ["ground", "rock", "water"]
        },
        "ground": {
            "weak": ["grass", "ice", "water"],
            "strong": ["electric", "poison", "rock", "steel"]
        },
        "ice": {
            "weak": ["fire", "fighting", "rock", "steel"],
            "strong": ["dragon", "flying", "grass", "ground"]
        },
        "normal": {
            "weak": ["fighting"],
            "strong": []
        },
        "poison": {
            "weak": ["ground", "psychic"],
            "strong": ["fairy", "grass"]
        },
        "psychic": {
            "weak": ["bug", "dark", "ghost"],
            "strong": ["fighting", "poison"]
        },
        "rock": {
            "weak": ["fighting", "grass", "ground", "steel", "water"],
            "strong": ["bug", "fire", "flying", "ice"]
        },
        "steel": {
            "weak": ["fighting", "fire", "ground"],
            "strong": ["fairy", "ice", "rock"]
        },
        "water": {
            "weak": ["electric", "grass"],
            "strong": ["fire", "ground", "rock"]
        }
    }

    def calculateDamage(self, attacker, defender, move):
        """ accepts Pkmn and PkmnMove objects """
        def calculateAttack():
            if move.damageClass == 'physical':
                return attacker.baseAtk
            else:
                return attacker.baseSpAtk
            
        def calculateDefense():
            if move.damageClass == 'physical':
                return defender.baseDef
            else:
                return defender.baseSpDef
            
        def calculateStab():
            multiplier = 1
            if move.moveType == attacker.firstType or move.moveType == attacker.secondType:
                multiplier == 1.5
            
            return multiplier
        
        def calculateStrengthWeakness():
            multiplier = 1
            attackerStrongAgainst = self.WEAKNESSCHART[move.moveType]['strong']
            attackerWeakAgainst = self.WEAKNESSCHART[move.moveType]['weak']
            if attackerStrongAgainst in defender.firstType:
                multiplier *= 2
            elif attackerWeakAgainst in defender.firstType:
                multiplier *= 0.5
            
            if attackerStrongAgainst in defender.secondType:
                multiplier *= 2
            if attackerWeakAgainst in defender.secondType:
                multiplier *= 1.5
            
            return multiplier
            
        attack = calculateAttack()
        defense = calculateDefense()
        stabModifier = calculateStab()
        typeModifier = calculateStrengthWeakness()

        damage = ((2.4 * move.power * (attack/defense) / 50) + 2) * stabModifier * typeModifier

        return damage
    
    def returnScaledPokemonCopy(pkmn, level):
        pkmnCopy = copy.copy(pkmn)

        pkmnCopy.hp = (pkmn.baseHP * 2 + 31) * (level/100) + 10 + level
        pkmnCopy.attack = (pkmn.baseAtk * 2 + 31) * (level/100) + 5
        pkmnCopy.defense = (pkmn.baseDef * 2 + 31) * (level/100) + 5
        pkmnCopy.spAttack = (pkmn.baseSpAtk * 2 + 31) * (level/100) + 5
        pkmnCopy.spDefense = (pkmn.baseAtk * 2 + 31) * (level/100) + 5
        pkmnCopy.speed = (pkmn.baseAtk * 2 + 31) * (level/100) + 5

        return pkmnCopy

    def battle(self, pkmn1, pkmn2):
        pokemon1 = self.returnScaledPokemonCopy(pkmn1)
        pokemon2 = self.returnScaledPokemonCopy(pkmn2)

        while pokemon1.hp > 0 and pokemon2.hp > 0:
            break

    



