import unittest
import unittest.mock as mock
from wtforms.validators import ValidationError
from speeddb import constants as cn, db, forms
from speeddb.models.user import User
from tests.base_test_case import BaseTestCase
from tests.constants import *

class FormsTestCase(BaseTestCase):
    def test_validate_url_youtube(self):
        form = forms.UploadForm()
        field_mock = mock.Mock(data=CLIP_URL_YOUTUBE)
        form.validate_url(field_mock)

    def test_validate_url_twitch(self):
        form = forms.UploadForm()
        field_mock = mock.Mock(data=CLIP_URL_TWITCH)
        form.validate_url(field_mock)

    def test_validate_url_twitter(self):
        form = forms.UploadForm()
        field_mock = mock.Mock(data=CLIP_URL_TWITTER)
        form.validate_url(field_mock)

    def test_validate_url_invalid(self):
        form = forms.UploadForm()
        field_mock = mock.Mock(data='https://github.com/Krankdud')
        with self.assertRaises(ValidationError):
            form.validate_url(field_mock)

    def test_validate_tags(self):
        form = forms.UploadForm()
        field_mock = mock.Mock(data=CLIP_TAGS)
        form.validate_tags(field_mock)

    def test_validate_tags_empty(self):
        form = forms.UploadForm()
        field_mock = mock.Mock(data='')
        form.validate_tags(field_mock)

    def test_validate_tags_invalid(self):
        form = forms.UploadForm()
        tags = 'tag1,tag2,tag3,' + 'a' * (cn.TAG_NAME_LENGTH + 1)
        field_mock = mock.Mock(data=tags)
        with self.assertRaises(ValidationError):
            form.validate_tags(field_mock)

    def test_validate_regular_user(self):
        self.register()

        form = forms.LoginFormWithBans(username=USER_NAME, password=USER_PASSWORD)
        self.assertTrue(form.validate())

    def test_validate_banned_user(self):
        self.register()
        user = User.query.get(1)
        user.banned = True
        db.session.add(user)
        db.session.commit()

        form = forms.LoginFormWithBans(username=USER_NAME, password=USER_PASSWORD)
        self.assertFalse(form.validate())

if __name__ == '__main__':
    unittest.main()