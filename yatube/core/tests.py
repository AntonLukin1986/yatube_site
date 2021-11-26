from django.test import TestCase, Client

from http import HTTPStatus

UNEXISTING_URL = '/unexisting_url/'


class ViewTestClass(TestCase):
    def setUP(self):
        self.client = Client()

    def test_error_page(self):
        response = self.client.get(UNEXISTING_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
