import shutil
import tempfile
import unittest
import unittest.mock as mock
import whoosh.writing
from speeddb import db, search
from speeddb.models.clips import Clip
from speeddb.models.tags import Tag
from speeddb.models.user import User
from tests.base_test_case import BaseTestCase
from tests.constants import *

class SearchTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.index_dir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.index_dir)

    @mock.patch('speeddb.search.index.create_in', autospec=True)
    def test_create_index(self, mock_create_in):
        search.create_index(self.index_dir)
        mock_create_in.assert_called()

    @mock.patch('speeddb.search.index.open_dir', autospec=True)
    @mock.patch('speeddb.search.index.exists_in', autospec=True)
    def test_create_index_already_exists(self, mock_exists_in, mock_open_dir):
        mock_exists_in.return_value = True
        search.create_index(self.index_dir)
        mock_open_dir.assert_called()

    def test_add_clip(self):
        user = User(username=USER_NAME, password=USER_PASSWORD, email=USER_EMAIL)
        tag1 = Tag(name="tag-1")
        tag2 = Tag(name="tag-2")
        clip = Clip(title=CLIP_TITLE, description=CLIP_DESCRIPTION, url=CLIP_URL_TWITTER)
        clip.user = user
        clip.tags = [tag1, tag2]
        db.session.add(clip)
        db.session.commit()

        search.create_index(self.index_dir)
        search.add_clip(clip)
        results = search.search_clips(CLIP_TITLE, 1)
        self.assertEqual(results.length, 1)
        self.assertEqual(results.clips[0].title, CLIP_TITLE)

    def test_add_clips(self):
        user = User(username=USER_NAME, password=USER_PASSWORD, email=USER_EMAIL)
        tag1 = Tag(name="tag-1")
        tag2 = Tag(name="tag-2")

        clips = []
        for i in range(3):
            clip = Clip(title=CLIP_TITLE, description=CLIP_DESCRIPTION, url=CLIP_URL_TWITTER)
            clip.user = user
            clip.tags = [tag1, tag2]
            clips.append(clip)
            db.session.add(clip)

        db.session.commit()
        
        search.create_index(self.index_dir)
        search.add_clips(clips)
        results = search.search_clips(CLIP_TITLE, 1)
        self.assertEqual(results.length, 3)

    def test_search_clips(self):
        user = User(username=USER_NAME, password=USER_PASSWORD, email=USER_EMAIL)
        tag1 = Tag(name="tag-1")
        tag2 = Tag(name="tag-2")
        clip = Clip(title=CLIP_TITLE, description=CLIP_DESCRIPTION, url=CLIP_URL_TWITTER)
        clip.user = user
        clip.tags = [tag1, tag2]
        db.session.add(clip)
        db.session.commit()

        search.create_index(self.index_dir)
        search.add_clip(clip)
        results = search.search_clips(CLIP_TITLE, 1)
        self.assertEqual(results.length, 1)
        self.assertEqual(results.clips[0].title, CLIP_TITLE)
        
        results = search.search_clips(CLIP_DESCRIPTION, 1)
        self.assertEqual(results.length, 1)
        self.assertEqual(results.clips[0].title, CLIP_TITLE)
        
        results = search.search_clips("tag 1", 1)
        self.assertEqual(results.length, 1)
        self.assertEqual(results.clips[0].title, CLIP_TITLE)
        
        results = search.search_clips(USER_NAME, 1)
        self.assertEqual(results.length, 1)
        self.assertEqual(results.clips[0].title, CLIP_TITLE)

if __name__ == '__main__':
    unittest.main()