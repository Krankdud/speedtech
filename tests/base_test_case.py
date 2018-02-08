import os
import shutil
import tempfile
import unittest
from speeddb import create_app, db, search
from speeddb.models.clips import Clip
from speeddb.models.tags import Tag
from tests.constants import *

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, db_path = tempfile.mkstemp()
        self.app = create_app(dict(
            TESTING=True,

            SQLALCHEMY_DATABASE_URI='sqlite:///' + db_path,
            WHOOSH_INDEX=tempfile.mkdtemp(),

            WTF_CSRF_ENABLED=False,

            USER_ENABLE_CONFIRM_EMAIL=False,
            USER_ENABLE_LOGIN_WITHOUT_CONFIRM_EMAIL=True,

            MAIL_SUPPRESS_SEND=True,

            ENABLE_LOGGING = False
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
        tag = Tag.query.filter_by(name=TAG_NAME).first()
        if tag is None:
            tag = Tag(name=TAG_NAME)
        clip.tags.append(tag)
        db.session.add(clip)
        db.session.commit()
        search.add_clip(clip)