from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    dateCreated = db.Column(db.Date, nullable=False, default=datetime.utcnow())
    favoritePkmn = db.Column(db.String(10))

    def __init__(self, userName, password):
        self.userName = userName
        self.password = generate_password_hash(password)