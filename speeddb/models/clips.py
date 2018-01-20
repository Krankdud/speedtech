from speeddb import constants as cn, db
from sqlalchemy.sql import func

clip_tags = db.Table('clip_tags',
    db.Column('clip_id', db.Integer, db.ForeignKey('clips.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Clip(db.Model):
    __tablename__ = 'clips'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(cn.CLIP_TITLE_LENGTH), nullable=False)
    description = db.Column(db.String(cn.CLIP_DESCRIPTION_LENGTH), nullable=True)
    time_created = db.Column(db.DateTime(), server_default=func.now())
    time_updated = db.Column(db.DateTime(), onupdate=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    url = db.Column(db.String(cn.CLIP_URL_LENGTH), nullable=False)

    tags = db.relationship('Tag', secondary=clip_tags, lazy='subquery', backref=db.backref('clips', lazy=True))