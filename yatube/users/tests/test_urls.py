from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from http import HTTPStatus

User = get_user_model()


class UsersPagesURLTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_status_code(self):
        """Проверяем доступность страниц."""
        pages_urls = {
            '/auth/signup/': 'signup',
            '/auth/login/': 'login',
            '/auth/password_change/': 'password_change',
            '/auth/password_change/done/': 'password_change_done',
            '/auth/password_reset/': 'password_reset',
            '/auth/password_reset/done/': 'password_reset_done',
            '/auth/reset/uidb64/token/': 'password_reset_confirm',
            '/auth/reset/done/': 'password_reset_complete',
            '/auth/logout/': 'logged_out'
        }
        for url, page in pages_urls.items():
            with self.subTest(field=page):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_template(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/uidb64/token/': 'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(adress=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
