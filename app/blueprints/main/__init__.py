from flask import Blueprint

main = Blueprint("main", __name__, template_folder="main_templates")

from app.blueprints.main import routes
