from flask import current_app
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from flask_user.forms import LoginForm, RegisterForm
from wtforms import IntegerField, RadioField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, URL, ValidationError
from wtforms.widgets import HiddenInput
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

    def validate_tags(self, tags_field):
        """ Validates that each tag is within the character limit. """

        tag_list = tags_field.data.split(',')
        for tag in tag_list:
            if len(tag) > cn.TAG_NAME_LENGTH:
                raise ValidationError('Tag must be less than %d characters' % cn.TAG_NAME_LENGTH)

class DeleteClipForm(FlaskForm):
    """ DeleteClipForm is used to delete a clip """
    clip_id = IntegerField(u'Clip ID', [DataRequired()], id='delete-clip-id', widget=HiddenInput())

class BanUserForm(FlaskForm):
    """ BanUserForm is used for banning a user """
    user_id = IntegerField(u'User ID', [DataRequired()], widget=HiddenInput())

class EditProfileForm(FlaskForm):
    """ EditProfileForm is the form used to update a user's profile """

    twitter = StringField(u'Twitter', [Length(max=cn.USER_TWITTER_LENGTH)])
    twitch = StringField(u'Twitch.tv', [Length(max=cn.USER_TWITCH_LENGTH)])
    youtube = StringField(u'YouTube', [Length(max=cn.USER_YOUTUBE_LENGTH)])
    speedruncom = StringField(u'speedrun.com', [Length(max=cn.USER_SPEEDRUNCOM_LENGTH)])
    discord = StringField(u'Discord', [Length(max=cn.USER_DISCORD_LENGTH)])

class ReportForm(FlaskForm):
    """ ReportForm is the form used by users to report inappropriate clips """

    clip_id = IntegerField(u'Clip ID', [DataRequired()], id='report-clip-id', widget=HiddenInput())
    reason = RadioField(u'Reason', [DataRequired()], id='report-reason', choices=[('content', 'Sexual or violent content'), ('not_speedrun', 'Not related to speedrunning'), ('spam', 'Spam'), ('other', 'Other')])
    description = TextAreaField(u'Description', [Length(max=cn.REPORT_DESCRIPTION_LENGTH)], id='report-description')

class RecaptchaRegisterForm(RegisterForm):
    """ RecaptchaRegisterForm is the register form from flask-user with recaptcha added to it """
    recaptcha = RecaptchaField()

class LoginFormWithBans(LoginForm):
    """ LoginFormWithBans is a flask-user LoginForm that checks if a user is banned while validating """
    def validate(self):
        valid_user = super().validate()
        if valid_user:
            user_manager = current_app.user_manager
            user = None
            user_email = None

            user = user_manager.find_user_by_username(self.username.data)
            if not user:
                user, user_email = user_manager.find_user_by_email(self.email.data)

            if user and user.banned:
                self.username.errors.append('%s is banned' % user.username)
                return False

        return valid_user