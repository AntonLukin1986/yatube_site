from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        Post.objects.create(
            author=cls.user,
            text='Тестовый текст'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает новую запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'author': 'NoName',
            'text': 'Тестовый текст нового поста'
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Валидная форма изменяет существующую запись в Post."""
        form_data = {
            'author': 'NoName',
            'text': 'Изменённый тестовый текст'
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=(1,)),
            data=form_data
        )
        post_to_edit = Post.objects.get(id=1)
        self.assertEqual(post_to_edit.text, 'Изменённый тестовый текст')

# Запуск теста:
# python yatube/manage.py test posts.tests.test_forms
