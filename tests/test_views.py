import os
import shutil
import tempfile
import unittest
import unittest.mock as mock
from flask import Markup
from speeddb import constants as cn, create_app, db
from speeddb.models.clips import Clip
from speeddb.models.user import User

CLIP_TITLE = 'Title'
CLIP_TITLE_EDIT = 'Editted Title'
CLIP_DESCRIPTION = 'Description'
CLIP_DESCRIPTION_EDIT = 'Editted Description'
CLIP_URL_YOUTUBE = 'https://www.youtube.com/watch?v=2VMgxLLbYEs'
CLIP_URL_TWITCH = 'https://clips.twitch.tv/DeafFrailWitchWoofer'
CLIP_URL_TWITTER = 'https://twitter.com/Krankdud/status/957171192980373507'
CLIP_TAGS = 'tag1,tag2,tag3'
CLIP_TAGS_EDIT = 'edit1,edit2,edit3'

USER_NAME = 'user'
USER_PASSWORD = 'Password1'
USER_EMAIL = 'user@email.com'
OTHER_USER_NAME = 'user2'
OTHER_USER_PASSWORD = 'Password1'
OTHER_USER_EMAIL = 'user2@email.com'

class ViewsTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, db_path = tempfile.mkstemp()
        self.app = create_app(dict(
            TESTING=True,

            SQLALCHEMY_DATABASE_URI='sqlite:///' + db_path,
            WHOOSH_INDEX=tempfile.mkdtemp(),

            WTF_CSRF_ENABLED=False,

            USER_ENABLE_CONFIRM_EMAIL=False,
            USER_ENABLE_LOGIN_WITHOUT_CONFIRM_EMAIL=True,

            MAIL_SUPPRESS_SEND=True
        ))
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()
        os.close(self.db_fd)
        shutil.rmtree(self.app.config['WHOOSH_INDEX'])

    def register(self, username=USER_NAME, email=USER_EMAIL, password=USER_PASSWORD):
        return self.client.post('/user/register', data=dict(username=username, email=email, password=password, retype_password=password), follow_redirects=True)

    def login(self, username=USER_NAME, password=USER_PASSWORD):
        return self.client.post('/user/sign-in', data=dict(username=username, password=password), follow_redirects=True)

    def create_test_clip(self, user_id=1):
        clip = Clip(title=CLIP_TITLE, description=CLIP_DESCRIPTION, url=CLIP_URL_YOUTUBE, user_id=user_id)
        db.session.add(clip)
        db.session.commit()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_upload_get(self):
        self.register()
        self.login()
        response = self.client.get('/upload', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Submit a clip', response.get_data(as_text=True))

    def test_upload_valid_clip(self):
        self.register()
        self.login()

        response = self.client.post('/upload', data=dict(title=CLIP_TITLE, description=CLIP_DESCRIPTION, url=CLIP_URL_YOUTUBE, tags=CLIP_TAGS), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(CLIP_TITLE, response.get_data(as_text=True))

        # Check that the clip was created
        clip = Clip.query.get(1)
        self.assertEqual(clip.title, CLIP_TITLE)
        self.assertEqual(clip.description, CLIP_DESCRIPTION)
        self.assertEqual(clip.url, CLIP_URL_YOUTUBE)

    def test_upload_invalid_clip(self):
        self.register()
        self.login()

        response = self.client.post('/upload', data=dict(title=CLIP_TITLE, description=CLIP_DESCRIPTION, url='a', tags=CLIP_TAGS), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Submit a clip', response.get_data(as_text=True))

        # Check that the clip was not created
        clip = Clip.query.get(1)
        self.assertIsNone(clip)

    def test_upload_invalid_clip_invalid_tags(self):
        self.register()
        self.login()

        generated_tags = 'a' * (cn.TAG_NAME_LENGTH + 1)
        response = self.client.post('/upload', data=dict(title=CLIP_TITLE, description=CLIP_DESCRIPTION, url=CLIP_URL_YOUTUBE, tags=generated_tags), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Submit a clip', response.get_data(as_text=True))

        # Check that the clip was not created
        clip = Clip.query.get(1)
        self.assertIsNone(clip)

    @mock.patch('speeddb.views.clip.oembed_cache.get', autospec=True)
    def test_show_clip(self, mock_get):
        mock_get.return_value = Markup()

        self.register()
        self.login()
        self.create_test_clip()

        response = self.client.get('/clip/1')
        self.assertEqual(response.status_code, 200)

        mock_get.assert_called_with(CLIP_URL_YOUTUBE)

    def test_show_clip_does_not_exist(self):
        response = self.client.get('/clip/100')
        self.assertEqual(response.status_code, 404)

    def test_edit_clip_get(self):
        self.register()
        self.login()
        self.create_test_clip()

        response = self.client.get('/clip/1/edit', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Edit your clip', response.get_data(as_text=True))

    def test_edit_clip(self):
        self.register()
        self.login()
        self.create_test_clip()

        response = self.client.post('/clip/1/edit', data=dict(title=CLIP_TITLE_EDIT, description=CLIP_DESCRIPTION_EDIT, url=CLIP_URL_TWITTER, tags=CLIP_TAGS_EDIT), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(CLIP_TITLE_EDIT, response.get_data(as_text=True))

        # Check if the clip was editted 
        clip = Clip.query.get(1)
        self.assertEqual(clip.title, CLIP_TITLE_EDIT)
        self.assertEqual(clip.description, CLIP_DESCRIPTION_EDIT)
        self.assertEqual(clip.url, CLIP_URL_TWITTER)

    def test_edit_clip_invalid(self):
        self.register()
        self.login()
        self.create_test_clip()

        response = self.client.post('/clip/1/edit', data=dict(title=CLIP_TITLE_EDIT, description=CLIP_DESCRIPTION_EDIT, url='a', tags=CLIP_TAGS_EDIT), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Edit your clip', response.get_data(as_text=True))

        # Check that the clip remained the same
        clip = Clip.query.get(1)
        self.assertEqual(clip.title, CLIP_TITLE)
        self.assertEqual(clip.description, CLIP_DESCRIPTION)
        self.assertEqual(clip.url, CLIP_URL_YOUTUBE)

    def test_edit_clip_incorrect_user(self):
        self.register()
        self.create_test_clip()
        self.register(username=OTHER_USER_NAME, password=OTHER_USER_PASSWORD, email=OTHER_USER_EMAIL)
        self.login(username=OTHER_USER_NAME, password=OTHER_USER_PASSWORD)

        response = self.client.get('/clip/1/edit', follow_redirects=True)
        self.assertEqual(response.status_code, 403)
        response = self.client.post('/clip/1/edit', data=dict(title=CLIP_TITLE_EDIT, description=CLIP_DESCRIPTION_EDIT, url='a', tags=CLIP_TAGS_EDIT), follow_redirects=True)
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()