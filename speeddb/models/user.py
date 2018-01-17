from flask_user import UserMixin
from speeddb import app, db
from speeddb.models.clips import Clip

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')

    # Email 
    # email = db.Column(db.String(255), unique=True, nullable=False)
    # confirmed_at = db.Column(db.DateTime())

    # Social media
    twitter = db.Column(db.String(255), nullable=True)
    twitch = db.Column(db.String(255), nullable=True)
    youtube = db.Column(db.String(255), nullable=True)
    discord = db.Column(db.String(255), nullable=True)
    speedruncom = db.Column(db.String(255), nullable=True)

    clips = db.relationship('Clip', backref='user', lazy=True)