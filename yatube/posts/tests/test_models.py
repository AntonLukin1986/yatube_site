from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User

COMMENT = 'Тестовый комментарий'
TITLE = 'Тестовая группа'
TEXT = 'Тестовый текст'
AUTHOR = 'Author'
NONAME = 'NoName'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=NONAME)
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=TITLE
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=TEXT
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text=COMMENT
        )
        cls.follow = Follow.objects.create(
            author=cls.author,
            user=cls.user
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает метод __str__."""
        models_expected = {
            self.group: self.group.title,
            self.post: f'Автор: {self.post.author.username}. '
                       f'Дата: {self.post.created}. '
                       f'Сообщество: {self.post.group}. '
                       f'Пост: {self.post.text[:15]}.',
            self.comment: f'Автор: {self.comment.author.username}. '
                          f'Создан: {self.comment.created}. '
                          f'Содержание: {self.comment.text[:15]}. '
                          f'Пост: {self.comment.post.id}.',
            self.follow: f'{self.user.username} подписан '
                         f'на {self.author.username}.'
        }
        for model, expected in models_expected.items():
            with self.subTest(field=model):
                self.assertEqual(str(model), expected)

    def test_model_Post_has_correct_help_text(self):
        """Проверяем, что у модели Post корректно работает help_text."""
        fields_expected = {
            'text': 'Текст нового поста',
            'group': 'Сообщество, к которому будет относиться пост'
        }
        for field, expected in fields_expected.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text, expected)

    def test_model_Post_has_correct_verbose_name(self):
        """Проверяем, что у модели Post корректно работает verbose_name."""
        fields_verbose = {
            'text': 'Текст поста',
            'created': 'Дата создания',
            'author': 'Автор',
            'group': 'Сообщество',
            'image': 'Изображение'
        }
        for field, expected in fields_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name, expected)
