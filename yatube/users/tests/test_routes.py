from django.test import TestCase
from django.urls import reverse


class RoutesURLTest(TestCase):
    def test_named_paths_match_with_explicit_urls(self):
        """Именованные пути совпадают с фактическими URL адресами."""
        cases = [
            ['signup', [], '/auth/signup/'],
            ['login', [], '/auth/login/'],
            ['logout', [], '/auth/logout/'],
            ['password_change', [], '/auth/password_change/'],
            ['password_change_done', [], '/auth/password_change/done/'],
            ['password_reset', [], '/auth/password_reset/'],
            ['password_reset_confirm',
             {'uidb64': 1, 'token': 2},
             '/auth/reset/1/2/'],
            ['password_reset_done', [], '/auth/password_reset/done/'],
            ['password_reset_complete', [], '/auth/reset/done/']
        ]
        for name, param, url in cases:
            with self.subTest(name=name):
                self.assertEqual(reverse(f'users:{name}', kwargs=param), url)
