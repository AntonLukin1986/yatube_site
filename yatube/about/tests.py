from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

AUTHOR_URL = reverse('about:author')
TECH_URL = reverse('about:tech')


class StaticPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest = Client()

    def test_routes(self):
        """Именованные пути совпадают с фактическими URL адресами."""
        cases = [
            ['author', '/about/author/'],
            ['tech', '/about/tech/']
        ]
        for name, url in cases:
            with self.subTest(name=name):
                self.assertEqual(reverse(f'about:{name}'), url)

    def test_pages_status_code(self):
        """Проверка доступности страниц."""
        urls = [AUTHOR_URL, TECH_URL]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest.get(url).status_code, HTTPStatus.OK
                )

    def test_urls_use_correct_templates(self):
        """Проверка использования URL-адресами соответствующих шаблов."""
        cases = [
            [AUTHOR_URL, 'about/author.html'],
            [TECH_URL, 'about/tech.html']
        ]
        for url, template in cases:
            with self.subTest(url=url):
                self.assertTemplateUsed(self.guest.get(url), template)
