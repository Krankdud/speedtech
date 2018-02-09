from flask_user import UserMixin
from speeddb import constants as cn, db
from speeddb.models.clips import Clip

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(cn.USER_NAME_LENGTH), unique=True, nullable=False)
    password = db.Column(db.String(cn.USER_PASSWORD_LENGTH), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')

    # Email 
    email = db.Column(db.String(cn.USER_EMAIL_LENGTH), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime())

    # Social media
    twitter = db.Column(db.String(cn.USER_TWITTER_LENGTH), nullable=True)
    twitch = db.Column(db.String(cn.USER_TWITCH_LENGTH), nullable=True)
    youtube = db.Column(db.String(cn.USER_YOUTUBE_LENGTH), nullable=True)
    discord = db.Column(db.String(cn.USER_DISCORD_LENGTH), nullable=True)
    speedruncom = db.Column(db.String(cn.USER_SPEEDRUNCOM_LENGTH), nullable=True)

    clips = db.relationship('Clip', backref='user', lazy='dynamic')