import unittest
from tests.base_test_case import BaseTestCase
from tests.constants import *

class ViewUserTestCase(BaseTestCase):
    def test_user_profile_page(self):
        self.register()
        response = self.client.get('/user/' + USER_NAME + '/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_user_profile_page_user_does_not_exist(self):
        response = self.client.get('/user/' + USER_NAME + '/1', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_user_profile_redirect(self):
        self.register()
        response_redirect = self.client.get('/user/' + USER_NAME, follow_redirects=True)
        self.assertEqual(response_redirect.status_code, 200)
        response_page = self.client.get('/user/' + USER_NAME + '/1', follow_redirects=True)
        self.assertEqual(response_page.status_code, 200)

        self.assertEqual(response_redirect.get_data(), response_page.get_data())

    def test_user_edit_profile_get(self):
        self.register()
        self.login()
        response = self.client.get('/user/edit-profile')
        self.assertEqual(response.status_code, 200)
    
    def test_user_edit_profile_post(self):
        self.register()
        self.login()

        before_response = self.client.get('/user/' + USER_NAME + '/1', follow_redirects=True)
        self.assertEqual(before_response.status_code, 200)

        response = self.client.post('/user/edit-profile', data=dict(twitter='@user'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        after_response = self.client.get('/user/' + USER_NAME + '/1', follow_redirects=True)
        self.assertEqual(after_response.status_code, 200)

        self.assertNotEqual(before_response.get_data(), after_response.get_data())

if __name__ == '__main__':
    unittest.main()