from flask import Blueprint
from flask_login import LoginManager
from app.models import User

account = Blueprint("account", __name__, template_folder="account_templates")

from app.blueprints.account import routes
