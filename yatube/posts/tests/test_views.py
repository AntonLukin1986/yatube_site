import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User
from posts.settings import PAGINATOR_PAGE

COMMENT = 'Тестовый комментарий'
SLUG = 'test-slug'
SLUG_OTHER = 'other-test-slug'
TEXT = 'Тестовый текст'
TEXT_OTHER = 'Другой тестовый текст'
TITLE = 'Тестовая группа'
TITLE_OTHER = 'Другая тестовая группа'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)

AUTHOR = 'Author'
AUTHOR_OTHER = 'OtherAuthor'
FOLLOWER = 'Подписчик'
UNFOLLOWER = 'НеПодписчик'

FOLLOW_URL = reverse('posts:profile_follow', args=[AUTHOR_OTHER])
FOLLOW_LIST_URL = reverse('posts:follow_index')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
GROUP_OTHER_URL = reverse('posts:group_list', args=[SLUG_OTHER])
INDEX_URL = reverse('posts:index')
PROFILE_URL = reverse('posts:profile', args=[AUTHOR])
PROFILE_OTHER_URL = reverse('posts:profile', args=[AUTHOR_OTHER])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[AUTHOR_OTHER])

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


def tearDownModule():
    shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.author_other = User.objects.create_user(username=AUTHOR_OTHER)
        cls.follower = User.objects.create_user(username=FOLLOWER)
        cls.unfollower = User.objects.create_user(username=UNFOLLOWER)
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG
        )
        cls.group_other = Group.objects.create(
            title=TITLE_OTHER,
            slug=SLUG_OTHER
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=TEXT,
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            author=cls.follower,
            post=cls.post,
            text=COMMENT
        )
        Follow.objects.create(
            author=cls.author,
            user=cls.follower
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.guest = Client()
        cls.auth_follower = Client()
        cls.auth_follower.force_login(cls.follower)
        cls.auth_unfollower = Client()
        cls.auth_unfollower.force_login(cls.unfollower)

    def test_pages_show_correct_context(self):
        """Шаблоны index, group_list, profile, post_detail и follow
        формируются с правильным контекстом."""
        urls = [
            INDEX_URL,
            GROUP_URL,
            PROFILE_URL,
            self.POST_DETAIL_URL,
            FOLLOW_LIST_URL
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.auth_follower.get(url)
                if url == self.POST_DETAIL_URL:
                    post = response.context['post']
                else:
                    post = response.context['page_obj'][0]
                    self.assertEqual(len(response.context['page_obj']), 1)
                self.assertEqual(post.id, self.post.id)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.image, 'posts/small.gif')

    def test_post_detail_page_has_correct_comments(self):
        """Проверка корректного отображения комментариев на странице поста."""
        response = self.auth_follower.get(self.POST_DETAIL_URL)
        comment = response.context['post'].comments.all()[0]
        self.assertEqual(len(response.context['post'].comments.all()), 1)
        self.assertEqual(comment.id, self.comment.id)
        self.assertEqual(comment.author, self.comment.author)
        self.assertEqual(comment.post, self.comment.post)
        self.assertEqual(comment.text, self.comment.text)

    def test_post_not_displayed_on_wrong_pages(self):
        """Пост отсутствует на странице другой группы, в профайле
        другого автора и в ленте не у подписчика."""
        urls = [
            PROFILE_OTHER_URL,
            GROUP_OTHER_URL,
            FOLLOW_LIST_URL
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertNotIn(
                    self.post,
                    self.auth_unfollower.get(url).context['page_obj']
                )

    def test_comments_not_displayed_on_wrong_post_page(self):
        """Комментарии не отображаются на странице другого поста."""
        self.post_other = Post.objects.create(
            author=self.author_other,
            text=TEXT_OTHER,
        )
        self.OTHER_POST_DETAIL_URL = reverse(
            'posts:post_detail', args=[self.post_other.id]
        )
        self.assertNotIn(
            self.comment,
            self.guest.get(self.OTHER_POST_DETAIL_URL).
            context['post'].comments.all()
        )

    def test_author_on_profile_page(self):
        """Автор на странице профиля."""
        self.assertEqual(
            self.author,
            self.guest.get(PROFILE_URL).context['author']
        )

    def test_group_on_group_page(self):
        """Граппа на странице групп-ленты."""
        group = self.guest.get(GROUP_URL).context['group']
        self.assertEqual(self.group, group)
        self.assertEqual(self.group.title, group.title)
        self.assertEqual(self.group.slug, group.slug)
        self.assertEqual(self.group.description, group.description)

    def test_index_page_cache(self):
        """Проверка кэширования списка постов главной страницы."""
        before = self.guest.get(INDEX_URL).content
        Post.objects.all().delete()
        after = self.guest.get(INDEX_URL).content
        self.assertEqual(after, before)
        cache.clear()
        cache_cleared = self.guest.get(INDEX_URL).content
        self.assertNotEqual(cache_cleared, after)

    def test_follow_author(self):
        """Авторизованный пользователь может подписаться на автора."""
        self.assertFalse(
            Follow.objects.filter(author=self.author_other, user=self.follower)
        )
        self.auth_follower.get(FOLLOW_URL)
        self.assertTrue(
            Follow.objects.filter(author=self.author_other, user=self.follower)
        )

    def test_unfollow_author(self):
        """Подписчик может отписаться от автора."""
        Follow.objects.create(author=self.author_other, user=self.follower)
        self.auth_follower.get(UNFOLLOW_URL)
        self.assertFalse(
            Follow.objects.filter(author=self.author_other, user=self.follower)
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.follower = User.objects.create_user(username=FOLLOWER)
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG
        )
        Post.objects.bulk_create(
            Post(author=cls.author, text=TEXT, group=cls.group)
            for _ in range(PAGINATOR_PAGE + 3)
        )
        Follow.objects.create(
            author=cls.author,
            user=cls.follower
        )
        cls.auth_follower = Client()
        cls.auth_follower.force_login(cls.follower)

    def test_first_and_second_pages_contain_required_posts_number(self):
        """На страницы выводится правильное число постов."""
        urls = [
            INDEX_URL,
            GROUP_URL,
            PROFILE_URL,
            FOLLOW_LIST_URL
        ]
        page_expected = {'': PAGINATOR_PAGE, '?page=2': 3}
        for url in urls:
            for page, expected in page_expected.items():
                with self.subTest(url=url + page):
                    response = self.auth_follower.get(url + page)
                    self.assertEqual(
                        len(response.context['page_obj']), expected
                    )
