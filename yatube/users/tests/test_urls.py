from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

User = get_user_model()

NONAME = 'NoName'
SIGNUP_URL = reverse('users:signup')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
PASSWORD_CHANGE_URL = reverse('users:password_change')
PASSWORD_CHANGE_DONE_URL = reverse('users:password_change_done')
PASSWORD_RESET = reverse('users:password_reset')
PASSWORD_RESET_CONFIRM = reverse(
    'users:password_reset_confirm', kwargs={'uidb64': 1, 'token': 2}
)
PASSWORD_RESET_DONE = reverse('users:password_reset_done')
PASSWORD_RESET_COMPLETE = reverse('users:password_reset_complete')


class UsersPagesURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=NONAME)
        cls.guest = Client()
        cls.authorized = Client()
        cls.authorized.force_login(cls.user)

    def test_pages_status_code_depending_on_client(self):
        """Доступность страниц в зависимости от прав клиента."""
        cases = [
            [SIGNUP_URL, self.guest, HTTPStatus.OK],
            [LOGIN_URL, self.guest, HTTPStatus.OK],
            [LOGOUT_URL, self.guest, HTTPStatus.OK],
            [PASSWORD_CHANGE_URL, self.guest, HTTPStatus.FOUND],
            [PASSWORD_CHANGE_URL, self.authorized, HTTPStatus.OK],
            [PASSWORD_CHANGE_DONE_URL, self.guest, HTTPStatus.FOUND],
            [PASSWORD_CHANGE_DONE_URL, self.authorized, HTTPStatus.OK],
            [PASSWORD_RESET, self.guest, HTTPStatus.OK],
            [PASSWORD_RESET_CONFIRM, self.guest, HTTPStatus.OK],
            [PASSWORD_RESET_DONE, self.guest, HTTPStatus.OK],
            [PASSWORD_RESET_COMPLETE, self.guest, HTTPStatus.OK]
        ]
        for url, client, code in cases:
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code, code)

    def test_pages_correct_redirection(self):
        """Страницы смены пароля корректно перенаправляют анонима."""
        urls = [PASSWORD_CHANGE_URL, PASSWORD_CHANGE_DONE_URL]
        for url in urls:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.guest.get(url), LOGIN_URL + '?next=' + url
                )

    def test_urls_use_correct_templates(self):
        """Использование URL-адресами соответствующих шаблов."""
        cases = [
            [SIGNUP_URL, self.guest, 'users/signup.html'],
            [LOGIN_URL, self.guest, 'users/login.html'],
            [LOGOUT_URL, self.guest, 'users/logged_out.html'],
            [PASSWORD_CHANGE_URL,
             self.authorized,
             'users/password_change_form.html'],
            [PASSWORD_CHANGE_DONE_URL,
             self.authorized,
             'users/password_change_done.html'],
            [PASSWORD_RESET, self.guest, 'users/password_reset_form.html'],
            [PASSWORD_RESET_CONFIRM,
             self.guest,
             'users/password_reset_confirm.html'],
            [PASSWORD_RESET_DONE,
             self.guest,
             'users/password_reset_done.html'],
            [PASSWORD_RESET_COMPLETE,
             self.guest,
             'users/password_reset_complete.html']
        ]
        for url, client, template in cases:
            with self.subTest(field=url):
                self.assertTemplateUsed(client.get(url), template)
