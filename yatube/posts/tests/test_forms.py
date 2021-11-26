import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User

# Создаем временную папку для медиа-файлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

AUTHOR = 'Author'
COMMENT = 'Тестовый комментарий'
NEW_POST_TEXT = 'Тестовый текст нового поста'
TEXT = 'Тестовый текст'
TEXT_EDITED = 'Изменённый тестовый текст'
TITLE = 'Тестовая группа'
SLUG = 'test-slug'
SLUG_OTHER = 'test-other-slug'
USER = 'User'
# Байт-последовательность картинки, состоящей
# из двух пикселей: белого и чёрного
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
INDEX_URL = reverse('posts:index')
LOGIN_URL = reverse('users:login') + '?next='
POST_CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', args=[AUTHOR])


def tearDownModule():
    # shutil - библиотека Python для управления файлами и директориями.
    # Метод shutil.rmtree удаляет директорию и всё её содержимое
    shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


# Переопределяем основную медиа папку на временную
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER)
        cls.user_author = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG
        )
        cls.group_other = Group.objects.create(
            title=TITLE,
            slug=SLUG_OTHER
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            group=cls.group,
            text=TEXT
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.COMMENT_URL = reverse('posts:add_comment', args=[cls.post.id])
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user_author)
        cls.not_author = Client()
        cls.not_author.force_login(cls.user)

    def test_valid_form_creates_post(self):
        """Валидная форма создает новую запись в Post."""
        existing_post_ids = set(
            Post.objects.all().values_list('id', flat=True)
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': NEW_POST_TEXT,
            'group': self.group_other.id,
            'image': uploaded
        }
        response = self.author.post(POST_CREATE_URL, data=form_data)
        created_posts = Post.objects.exclude(id__in=existing_post_ids)
        self.assertEqual(created_posts.count(), 1)
        new_post = created_posts[0]
        self.assertEqual(new_post.author, self.user_author)
        self.assertEqual(new_post.group.id, form_data['group'])
        self.assertEqual(new_post.image, 'posts/small.gif')
        self.assertEqual(new_post.text, form_data['text'])
        self.assertRedirects(response, PROFILE_URL)

    def test_unauthorized_user_unable_create_post(self):
        """Аноним не может создать новый пост."""
        existing_post_ids = set(
            Post.objects.all().values_list('id', flat=True)
        )
        uploaded = SimpleUploadedFile(
            name='small_1.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': NEW_POST_TEXT,
            'group': self.group_other.id,
            'image': uploaded
        }
        response = self.guest.post(POST_CREATE_URL, data=form_data)
        created_posts = Post.objects.exclude(id__in=existing_post_ids)
        self.assertFalse(created_posts)
        self.assertRedirects(response, LOGIN_URL + POST_CREATE_URL)

    def test_valid_form_edits_post(self):
        """Валидная форма изменяет существующую запись в Post."""
        uploaded = SimpleUploadedFile(
            name='small_2.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group_other.id,
            'text': TEXT_EDITED,
            'image': uploaded
        }
        response = self.author.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        edited_post = response.context.get('post')
        self.assertEqual(edited_post.author, self.post.author)
        self.assertEqual(edited_post.group.id, form_data['group'])
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.image, 'posts/small_2.gif')
        self.assertRedirects(response, self.POST_DETAIL_URL)

    def test_unauthorized_users_unable_edit_post(self):
        """Аноним и не автор не могут редактировать чужой пост."""
        uploaded = SimpleUploadedFile(
            name='small_3.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group_other.id,
            'text': TEXT_EDITED,
            'image': uploaded
        }
        clients = [self.guest, self.not_author]
        for client in clients:
            with self.subTest(client=client):
                response = self.client.post(
                    self.POST_EDIT_URL,
                    data=form_data
                )
                posts_edit_attempt = Post.objects.filter(
                    id=self.post.id,
                    author=self.post.author,
                    group=self.post.group,
                    text=self.post.text,
                    image=self.post.image
                )
                self.assertEqual(posts_edit_attempt.count(), 1)
                self.assertRedirects(response, LOGIN_URL + self.POST_EDIT_URL)

    def test_post_create_template_shows_correct_context(self):
        """Шаблон post_create.html при создании и редактировании поста
        формируется с правильным контекстом."""
        urls = [POST_CREATE_URL,
                self.POST_EDIT_URL]
        for url in urls:
            response = self.author.get(url)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
                'image': forms.fields.ImageField
            }
            for field, expected in form_fields.items():
                with self.subTest(field=field):
                    form_field = response.context['form'].fields[field]
                    self.assertIsInstance(form_field, expected)

    def test_creation_comment(self):
        """Валидная форма создаёт новый комментарий.
        Аноним не може комментировать посты."""
        existing_comment_ids = set(
            Comment.objects.all().values_list('id', flat=True)
        )
        form_data = {'text': COMMENT}
        clients = [self.guest, self.author]
        for client in clients:
            with self.subTest(client=client):
                response = client.post(self.COMMENT_URL, data=form_data)
                comments = Comment.objects.exclude(id__in=existing_comment_ids)
                if client == self.guest:
                    self.assertFalse(comments)
                    self.assertRedirects(
                        response, LOGIN_URL + self.COMMENT_URL
                    )
                else:
                    self.assertEqual(comments.count(), 1)
                    comment = comments[0]
                    self.assertEqual(comment.author, self.user_author)
                    self.assertEqual(comment.text, form_data['text'])
                    self.assertEqual(comment.post, self.post)
                    self.assertRedirects(response, self.POST_DETAIL_URL)

    def test_comment_create_page_shows_correct_context(self):
        """Шаблон post_detail.html при создании комментария
        формируется с правильным контекстом."""
        response = self.author.get(self.POST_DETAIL_URL)
        form_field = {'text': forms.fields.CharField}
        self.assertIsInstance(
            response.context['form'].fields['text'], form_field['text']
        )
