from app import app
from flask_login import current_user
from app.blueprints.pokedex.Pokedex import Pokedex

@app.context_processor
def injectFavoriteSprite():
    if current_user.is_authenticated and current_user.favoritePkmn != None:
        pokedex = Pokedex()
        favoritePkmn = current_user.favoritePkmn.split(',')
        pkmnID, spriteType = favoritePkmn[0], False if favoritePkmn[1] == 'd' else True

        favoriteSprite = pokedex.returnPokemonData(pkmnID, favoriteSprite=True, shiny=spriteType)
    else:
        favoriteSprite = None
    return dict(favoriteSprite=favoriteSprite)