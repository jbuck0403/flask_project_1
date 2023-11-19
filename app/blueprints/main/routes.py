from ..pokedex.Pokedex import Pokedex
from . import main

@main.route("/", methods=['GET', 'POST'])
def landingPage():
    pokedex = Pokedex()
    
    # pokedex.populateUnownAlphabetDB() # populate unownLetters db
    
    return pokedex.unownMessage(None, "welcome",'landingPage.jinja')