from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

import datetime as dt

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Сообщество',
            slug='test-slug',
        )
        Group.objects.create(
            title='Другое сообщество',
            slug='test-slug-other'
        )
        Post.objects.create(
            author=cls.user,
            text='Текст тестового поста',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'NoName'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': '1'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': '1'}
            ): 'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html'
            }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        fields_values = {first_object.group.title: 'Сообщество',
                         first_object.text: 'Текст тестового поста'}
        for field, value in fields_values.items():
            with self.subTest(field=field):
                self.assertEqual(field, value)

    def test_group_list_page_shows_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        response = self.guest_client.\
            get(reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        first_object = response.context['page_obj'][0]
        post_group_0 = first_object.group.slug
        self.assertEqual(post_group_0, 'test-slug')

    def test_profile_page_shows_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.guest_client.\
            get(reverse('posts:profile', kwargs={'username': 'NoName'}))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        self.assertEqual(post_author_0, 'NoName')

    def test_post_detail_page_shows_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response = self.guest_client.\
            get(reverse('posts:post_detail', kwargs={'post_id': '1'}))
        first_object = response.context.get('post')
        post_id_0 = first_object.id
        self.assertEqual(post_id_0, 1)

    def test_post_create_and_edit_pages_show_correct_context(self):
        """Шаблон post_create.html сформирован с правильным контекстом."""
        urls = [reverse('posts:post_create'),
                reverse('posts:post_edit', kwargs={'post_id': 1})]
        for url in urls:
            response = self.authorized_client.get(url)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField
            }
            for field, expected in form_fields.items():
                with self.subTest(field=field):
                    form_field = response.context['form'].fields[field]
                    self.assertIsInstance(form_field, expected)

    def post_with_group_displays_in_the_required_pages(self):
        """Пост, отнесённый к сообществу, отображается на требуемых страницах и
           не виден на странице иного сообщества."""
        urls = [reverse('posts:index'),
                reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
                reverse('posts:profile', kwargs={'username': 'NoName'})]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.context['page_obj'][0].text,
                    'Текст тестового поста'
                    )
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug-other'})
            )
        self.assertFalse(response.context.get('page_obj'))


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Сообщество',
            slug='test-slug',
        )
        for i in range(1, 14):
            Post.objects.create(
                author=cls.user,
                text=f'Текст тестового поста №{i}',
                group=cls.group
            )
            post = Post.objects.get(id=i)
            post.pub_date = dt.datetime.now()
            post.save()

    def setUp(self):
        self.guest_client = Client()

    def test_first_and_second_pages_contains_required_posts(self):
        """Проверяем, что на страницы выводится правильное число постов.
           Содержимое постов на странице соответствует ожиданиям"""
        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'NoName'})
        ]
        expect_page = {10: '', 3: '?page=2'}
        for url in urls:
            for expect, page in expect_page.items():
                with self.subTest(url=url + page):
                    response = self.guest_client.get(url + page)
                    self.assertEqual(len(response.context['page_obj']), expect)
                    self.assertEqual(
                        response.context['page_obj'][0].text,
                        'Текст тестового поста №' + (
                            '13' if page == '' else '3')
                            )

# Запуск конкретного теста:
# python yatube/manage.py test posts.tests.test_views.<имя класса>.<имя теста>
