import unittest
import unittest.mock as mock
from tests.base_test_case import BaseTestCase
from tests.constants import *

class ViewReportTestCase(BaseTestCase):
    @mock.patch('speeddb.views.report.mail.send', autospec=True)
    def test_report_success(self, mock_send):
        response = self.client.post('/report', data=dict(clip_id=CLIP_ID, reason=REPORT_REASON, description=REPORT_DESCRIPTION), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        mock_send.assert_called()

    @mock.patch('speeddb.views.report.mail.send', autospec=True)
    def test_report_invalid_form(self, mock_send):
        response = self.client.post('/report', data=dict(clip_id=CLIP_ID, reason='a', description=REPORT_DESCRIPTION), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        mock_send.assert_not_called()

if __name__ == '__main__':
    unittest.main()