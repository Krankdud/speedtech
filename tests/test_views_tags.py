import json
import unittest
from speeddb import db
from speeddb.models.tags import Tag
from tests.base_test_case import BaseTestCase
from tests.constants import *

class ViewTagsTestCase(BaseTestCase):
    def test_get_tags(self):
        tag = Tag(name=TAG_NAME)
        db.session.add(tag)
        db.session.commit()

        response = self.client.get('/_get-tags', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        tag_names = json.loads(response.get_data())
        self.assertEqual(tag_names[0], TAG_NAME)

if __name__ == '__main__':
    unittest.main()