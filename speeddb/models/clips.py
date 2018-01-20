from speeddb import constants as cn, db

clip_tags = db.Table('clip_tags',
    db.Column('clip_id', db.Integer, db.ForeignKey('clips.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Clip(db.Model):
    __tablename__ = 'clips'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(cn.CLIP_TITLE_LENGTH), nullable=False)
    description = db.Column(db.String(cn.CLIP_DESCRIPTION_LENGTH), nullable=True)
    upload_date = db.Column(db.DateTime(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    url = db.Column(db.String(cn.CLIP_URL_LENGTH), nullable=False)

    tags = db.relationship('Tag', secondary=clip_tags, lazy='subquery', backref=db.backref('clips', lazy=True))