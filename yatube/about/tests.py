from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_status_code(self):
        """Проверяем доступность страниц."""
        pages_urls = {
            'authorpage': '/about/author/',
            'techpage': '/about/tech/'
        }
        for page, url in pages_urls.items():
            with self.subTest(field=page):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
            }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
