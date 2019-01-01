import unittest
import unittest.mock as mock
from tests.base_test_case import BaseTestCase
from tests.constants import *

class ViewSearchTestCase(BaseTestCase):
    def test_show_tag_page(self):
        self.register()
        self.create_test_clip()
        response = self.client.get('/tag/' + TAG_NAME + '/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_show_tag_page_missing_tag(self):
        response = self.client.get('/tag/does-not-exist/1', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_show_tag_redirect(self):
        self.register()
        self.create_test_clip()
        response_redirect = self.client.get('/tag/' + TAG_NAME, follow_redirects=True)
        self.assertEqual(response_redirect.status_code, 200)

        response_tag_page = self.client.get('/tag/' + TAG_NAME + '/1', follow_redirects=True)
        self.assertEqual(response_tag_page.status_code, 200)

        self.assertEqual(response_redirect.get_data(), response_tag_page.get_data())

    @mock.patch('speeddb.pagination.oembed_cache.get')
    def test_search_clips(self, mock_oembed_cache):
        mock_oembed_cache.return_value = ''

        self.register()
        self.create_test_clip()
        response = self.client.get('/search?q=' + CLIP_TITLE, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        mock_oembed_cache.assert_called()

    def test_search_clips_invalid_page(self):
        response = self.client.get('/search?q=' + CLIP_TITLE + '&page=a', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_search_clips_redirect_to_index(self):
        response_search = self.client.get('/search', follow_redirects=True)
        self.assertEqual(response_search.status_code, 200)
        response_index = self.client.get('/')
        self.assertEqual(response_index.status_code, 200)
        self.assertEqual(response_search.get_data(), response_index.get_data())

if __name__ == '__main__':
    unittest.main()