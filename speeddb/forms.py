from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, URL, ValidationError
from speeddb import constants as cn

class UploadForm(FlaskForm):
    """ UploadForm is the form used to upload clips to the database. 
    
    Fields:
    Title - Title of the clip. Required.
    Description - Description of the clip.
    URL - URL to the video. Required.
    Tags - Comma separated list of tags. 
    """ 

    title = StringField(u'Title', [DataRequired(), Length(max=cn.CLIP_TITLE_LENGTH)])
    description = TextAreaField(u'Description', [Length(max=cn.CLIP_DESCRIPTION_LENGTH)])
    url = StringField(u'URL', [DataRequired(), URL(), Length(max=cn.CLIP_URL_LENGTH)])
    tags = StringField(u'Tags')

    def validate_tags(form, field):
        """ Validates that each tag is within the character limit. """

        tag_list = field.data.split(',')
        for tag in tag_list:
            if len(tag) > cn.TAG_NAME_LENGTH:
                raise ValidationError('Tag must be less than %d characters' % cn.TAG_NAME_LENGTH)

class EditProfileForm(FlaskForm):
    """ EditProfileForm is the form used to update a user's profile """

    twitter = StringField(u'Twitter', [Length(max=cn.USER_TWITTER_LENGTH)])
    twitch = StringField(u'Twitch.tv', [Length(max=cn.USER_TWITCH_LENGTH)])
    youtube = StringField(u'YouTube', [Length(max=cn.USER_YOUTUBE_LENGTH)])
    speedruncom = StringField(u'speedrun.com', [Length(max=cn.USER_SPEEDRUNCOM_LENGTH)])
    discord = StringField(u'Discord', [Length(max=cn.USER_DISCORD_LENGTH)])