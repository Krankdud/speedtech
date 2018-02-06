import unittest
import unittest.mock as mock
from flask import Markup
from speeddb import constants as cn
from speeddb.models.clips import Clip
from speeddb.tests.base_test_case import BaseTestCase
from speeddb.tests.constants import *

class ViewClipTestCase(BaseTestCase):
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