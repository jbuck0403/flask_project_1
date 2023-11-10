from flask import Flask
from config import Config
from flask_login import LoginManager
from app.models import db
from flask_migrate import Migrate
from app.models import User

app = Flask(__name__)
app.config.from_object(Config)

loginManager = LoginManager()

loginManager.init_app(app)
db.init_app(app)

migrate = Migrate(app, db)

@loginManager.user_loader
def loadUser(user_id):
    return User.query.get(user_id)

from app import routes