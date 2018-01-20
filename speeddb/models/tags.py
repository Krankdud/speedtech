from speeddb import constants as cn, db

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(cn.TAG_NAME_LENGTH), nullable=False)