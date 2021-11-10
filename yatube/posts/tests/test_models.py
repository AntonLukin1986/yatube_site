from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст тестового поста',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        post = PostModelTest.post
        model_names = {
            group: 'Тестовая группа',
            post: 'Текст тестового поста'[:15]
        }
        for model in model_names.keys():
            with self.subTest(field=model):
                self.assertEqual(str(model), model_names[model])

    def test_model_Post_have_correct_help_text(self):
        """Проверяем, что у модели Post корректно работает help_text."""
        post = PostModelTest.post
        field_helps = {
            'text': 'Введите текст поста',
            'group': 'Выберите cообщество'
        }
        for field, expected_value in field_helps.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_model_Post_have_correct_verbose_name(self):
        """Проверяем, что у модели Post корректно работает verbose_name."""
        post = PostModelTest.post
        field_verbose = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Сообщество'
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)
