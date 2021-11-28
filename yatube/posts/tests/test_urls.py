from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

from posts.models import Group, Post, User

AUTHOR = 'Author'
NONAME = 'NoName'
SLUG = 'test-slug'

FOLLOW_URL = reverse('posts:profile_follow', args=[AUTHOR])
FOLLOW_LIST_URL = reverse('posts:follow_index')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
INDEX_URL = reverse('posts:index')
LOGIN_URL = reverse('users:login') + '?next='
POST_CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', args=[AUTHOR])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[AUTHOR])


class PostPagesURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username=AUTHOR)
        cls.not_author = User.objects.create_user(username=NONAME)
        cls.group = Group.objects.create(slug=SLUG)
        cls.post = Post.objects.create(author=cls.user_author)
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user_author)
        cls.other = Client()
        cls.other.force_login(cls.not_author)

    def test_pages_status_code_depending_on_client(self):
        """Проверка доступности страниц в зависимости от прав клиента."""
        cases = [
            [INDEX_URL, self.guest, HTTPStatus.OK],
            [GROUP_URL, self.guest, HTTPStatus.OK],
            [PROFILE_URL, self.guest, HTTPStatus.OK],
            [self.POST_DETAIL_URL, self.guest, HTTPStatus.OK],
            [POST_CREATE_URL, self.guest, HTTPStatus.FOUND],
            [POST_CREATE_URL, self.other, HTTPStatus.OK],
            [self.POST_EDIT_URL, self.guest, HTTPStatus.FOUND],
            [self.POST_EDIT_URL, self.other, HTTPStatus.FOUND],
            [self.POST_EDIT_URL, self.author, HTTPStatus.OK],
            [FOLLOW_LIST_URL, self.guest, HTTPStatus.FOUND],
            [FOLLOW_LIST_URL, self.other, HTTPStatus.OK],
            [FOLLOW_URL, self.guest, HTTPStatus.FOUND],
            [FOLLOW_URL, self.other, HTTPStatus.FOUND],
            [FOLLOW_URL, self.author, HTTPStatus.FOUND],
            [UNFOLLOW_URL, self.guest, HTTPStatus.FOUND],
            [UNFOLLOW_URL, self.other, HTTPStatus.FOUND],
            [UNFOLLOW_URL, self.author, HTTPStatus.NOT_FOUND]
        ]
        for url, client, code in cases:
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code, code)

    def test_create_and_edit_pages_correct_redirection(self):
        """Страницы корректно перенаправляют пользователей."""
        cases = [
            [POST_CREATE_URL, self.guest, LOGIN_URL + POST_CREATE_URL],
            [self.POST_EDIT_URL, self.guest, LOGIN_URL + self.POST_EDIT_URL],
            [self.POST_EDIT_URL, self.other, self.POST_DETAIL_URL],
            [FOLLOW_LIST_URL, self.guest, LOGIN_URL + FOLLOW_LIST_URL],
            [FOLLOW_URL, self.guest, LOGIN_URL + FOLLOW_URL],
            [FOLLOW_URL, self.other, PROFILE_URL],
            [FOLLOW_URL, self.author, PROFILE_URL],
            [UNFOLLOW_URL, self.guest, LOGIN_URL + UNFOLLOW_URL],
            [UNFOLLOW_URL, self.other, PROFILE_URL]
        ]
        for url, client, expected_url in cases:
            with self.subTest(url=url, client=client):
                self.assertRedirects(client.get(url), expected_url)

    def test_urls_use_correct_templates(self):
        """Проверка использования URL-адресами соответствующих шаблов."""
        cases = [
            [INDEX_URL, self.guest, 'posts/index.html'],
            [GROUP_URL, self.guest, 'posts/group_list.html'],
            [PROFILE_URL, self.guest, 'posts/profile.html'],
            [self.POST_DETAIL_URL, self.guest, 'posts/post_detail.html'],
            [POST_CREATE_URL, self.other, 'posts/post_create.html'],
            [self.POST_EDIT_URL, self.author, 'posts/post_create.html'],
            [FOLLOW_LIST_URL, self.other, 'posts/follow.html']
        ]
        for url, client, template in cases:
            with self.subTest(field=url):
                self.assertTemplateUsed(client.get(url), template)
