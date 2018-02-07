import unittest
import unittest.mock as mock
from speeddb import pagination
from speeddb.models.clips import Clip
from speeddb.models.tags import Tag
from tests.constants import *

class TestPagination(unittest.TestCase):
    def test_get_page_count(self):
        self.assertEqual(pagination.get_page_count(0, clips_per_page=10), 0)
        self.assertEqual(pagination.get_page_count(1, clips_per_page=10), 1)
        self.assertEqual(pagination.get_page_count(10, clips_per_page=10), 1)
        self.assertEqual(pagination.get_page_count(11, clips_per_page=10), 2)

    @mock.patch('speeddb.pagination.oembed_cache.get', autospec=True)
    def test_get_clips_on_page(self, mock_get):
        mock_get.return_value = ''

        clips = []
        for i in range(51):
            clips.append(Clip(title='%d' % i, description=CLIP_DESCRIPTION, url=CLIP_URL_TWITTER))

        # Check that the clips on each page corresponds to the correct clip
        clips_on_page = pagination.get_clips_on_page(clips, 1, 10)
        for i in range(10):
            self.assertEqual(clips_on_page[i].title, '%d' % i)
        clips_on_page = pagination.get_clips_on_page(clips, 2, 10)
        for i in range(10):
            self.assertEqual(clips_on_page[i].title, '%d' % (i + 10))
        clips_on_page = pagination.get_clips_on_page(clips, 3, 10)
        for i in range(10):
            self.assertEqual(clips_on_page[i].title, '%d' % (i + 20))
        clips_on_page = pagination.get_clips_on_page(clips, 4, 10)
        for i in range(10):
            self.assertEqual(clips_on_page[i].title, '%d' % (i + 30))
        clips_on_page = pagination.get_clips_on_page(clips, 5, 10)
        for i in range(10):
            self.assertEqual(clips_on_page[i].title, '%d' % (i + 40))

        # Check that the last page only has 1 clip
        clips_on_page = pagination.get_clips_on_page(clips, 6, 10)
        self.assertEqual(len(clips_on_page), 1)
        self.assertEqual(clips_on_page[0].title, '%d' % 50)

        # Check that any page after the last one will have no clips
        clips_on_page = pagination.get_clips_on_page(clips, 7, 10)
        self.assertEqual(len(clips_on_page), 0)

if __name__ == '__main__':
    unittest.main()