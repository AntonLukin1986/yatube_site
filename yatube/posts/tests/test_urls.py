from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class PostPagesURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='author')
        cls.user_not_author = User.objects.create_user(username='NoName')
        Group.objects.create(
            slug='test-slug',
        )
        Post.objects.create(
            author=cls.user_author,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostPagesURLTest.user_author)
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesURLTest.user_not_author)

    def test_pages_status_code(self):
        """Проверяем доступность страниц."""
        pages_urls = {
            '/': 'index',
            '/group/test-slug/': 'group_list',
            '/profile/author/': 'profile',
            '/posts/1/': 'post_detail',
            '/posts/1/edit/': 'post_edit',
            '/create/': 'post_create',
            '/unexisting_page/': 'unexisting_page'
        }
        for url, page in pages_urls.items():
            with self.subTest(field=page):
                if url == '/posts/1/edit/':
                    response = self.authorized_client_author.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                elif url == '/create/':
                    response = self.authorized_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                elif url == '/unexisting_page/':
                    response = self.guest_client.get(url)
                    self.assertEqual(
                        response.status_code, HTTPStatus.NOT_FOUND
                        )
                else:
                    response = self.guest_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_template(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(adress=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

        response = self.authorized_client_author.get(
            '/posts/1/edit/'
            )
        self.assertTemplateUsed(response, 'posts/create_post.html')

        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

# Запуск конкретного теста:
# python yatube/manage.py test posts.tests.test_urls.PostPagesURLTest.<имя теста>
