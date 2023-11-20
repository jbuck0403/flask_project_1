from flask import Flask
from config import Config
from app.models import db, User
from flask_login import LoginManager
from flask_migrate import Migrate

# Blueprint imports
from app.blueprints.account import account
from app.blueprints.main import main
from app.blueprints.pokedex import pokedexBP

app = Flask(__name__)
app.config.from_object(Config)

loginManager = LoginManager()
loginManager.init_app(app)

db.init_app(app)
migrate = Migrate(app, db)


@loginManager.user_loader
def loadUser(user_id):
    return User.query.get(user_id)


app.register_blueprint(account)
app.register_blueprint(main)
app.register_blueprint(pokedexBP)

from app import routes
