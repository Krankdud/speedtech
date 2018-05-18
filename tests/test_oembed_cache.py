import shutil
import tempfile
import time
import unittest
import unittest.mock as mock
from werkzeug.contrib.cache import SimpleCache, FileSystemCache
from speeddb import oembed_cache
from tests.constants import *

class OembedCacheTestCase(unittest.TestCase):
    def test_init_simple_cache(self):
        oembed_cache.init_cache()
        self.assertTrue(isinstance(oembed_cache.cache, SimpleCache))

    def test_init_file_cache(self):
        temp_dir = tempfile.mkdtemp()
        oembed_cache.init_cache(cache_type='file', cache_dir=temp_dir)
        self.assertTrue(isinstance(oembed_cache.cache, FileSystemCache))
        shutil.rmtree(temp_dir)

    @mock.patch('speeddb.oembed_cache.PyEmbed', autospec=True)
    def test_get_not_in_cache(self, mock_pyembed):
        mock_pyembed.return_value.embed.return_value = OEMBED_MARKUP

        oembed_cache.init_cache()
        markup = oembed_cache.get(CLIP_URL_TWITTER)
        mock_pyembed.return_value.embed.assert_called_with(CLIP_URL_TWITTER)
        self.assertEqual(markup.striptags(), OEMBED_MARKUP)

    @mock.patch('speeddb.oembed_cache.PyEmbed', autospec=True)
    def test_get_in_cache(self, mock_pyembed):
        mock_pyembed.return_value.embed.return_value = OEMBED_MARKUP

        oembed_cache.init_cache()
        oembed_cache.get(CLIP_URL_TWITTER)
        mock_pyembed.return_value.embed.assert_called_with(CLIP_URL_TWITTER)

        mock_pyembed.return_value.embed.reset_mock()

        markup = oembed_cache.get(CLIP_URL_TWITTER)
        mock_pyembed.return_value.embed.assert_not_called()
        self.assertEqual(markup.striptags(), OEMBED_MARKUP)

    @mock.patch('speeddb.oembed_cache.PyEmbed', autospec=True)
    def test_get_cache_timeout(self, mock_pyembed):
        mock_pyembed.return_value.embed.return_value = OEMBED_MARKUP

        oembed_cache.init_cache(timeout=1)
        oembed_cache.get(CLIP_URL_TWITTER)
        mock_pyembed.return_value.embed.assert_called_with(CLIP_URL_TWITTER)

        time.sleep(2)

        markup = oembed_cache.get(CLIP_URL_TWITTER)
        mock_pyembed.return_value.embed.assert_called_with(CLIP_URL_TWITTER)
        self.assertEqual(markup.striptags(), OEMBED_MARKUP)


if __name__ == '__main__':
    unittest.main()
