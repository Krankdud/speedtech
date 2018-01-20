from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, URL
from speeddb import constants as cn

class UploadForm(FlaskForm):
    title = StringField(u'Title', [DataRequired(), Length(max=cn.CLIP_TITLE_LENGTH)])
    description = TextAreaField(u'Description', [Length(max=cn.CLIP_DESCRIPTION_LENGTH)])
    url = StringField(u'URL', [DataRequired(), URL(), Length(max=cn.CLIP_URL_LENGTH)])