from app import app
from flask_login import current_user, login_required
from app.blueprints.pokedex.Pokedex import Pokedex


@app.context_processor
def injectFavoriteSprite():
    if current_user.is_authenticated and current_user.favoritePkmn != None:
        pokedex = Pokedex()
        favoritePkmn = current_user.favoritePkmn.split(",")
        pkmnID, spriteType = favoritePkmn[0], False if favoritePkmn[1] == "d" else True

        favoriteSprite = pokedex.returnPokemonSprite(pkmnID, shiny=spriteType)
    else:
        favoriteSprite = "./static/masterball_transparent.png"
    return dict(favoriteSprite=favoriteSprite)
