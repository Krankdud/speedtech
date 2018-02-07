import unittest
import unittest.mock as mock
from wtforms.validators import ValidationError
from speeddb import constants as cn, forms
from tests.base_test_case import BaseTestCase
from tests.constants import *

class FormsTestCase(BaseTestCase):
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

if __name__ == '__main__':
    unittest.main()