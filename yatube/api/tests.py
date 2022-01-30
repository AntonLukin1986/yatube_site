from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from api.serializers import PostSerializer
from posts.models import Group, Post, User

AUTHOR = 'Author'
SLUG = 'test-slug'

POST_1_TEXT = 'Текст поста №1'
POST_2_TEXT = 'Текст поста №2'
POST_LIST_URL = reverse('post-list')


class PostApiTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(slug=SLUG)
        cls.post_1 = Post.objects.create(
            author=cls.user_author,
            text=POST_1_TEXT,
            group=cls.group
        )
        cls.post_2 = Post.objects.create(
            author=cls.user_author, text=POST_2_TEXT
        )
        cls.POST_DETAIL_URL = reverse('post-detail', args=[cls.post_1.id])

    def test_get_list(self):
        response = self.client.get(POST_LIST_URL)
        serializer_data = PostSerializer(
            [self.post_1, self.post_2], many=True
        ).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_detail(self):
        response = self.client.get(self.POST_DETAIL_URL)
        serializer_data = PostSerializer(self.post_1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)


class PostSerializerTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(slug=SLUG)
        cls.post_1 = Post.objects.create(
            author=cls.user_author,
            text=POST_1_TEXT,
            group=cls.group
        )
        cls.post_2 = Post.objects.create(
            author=cls.user_author,
            text=POST_2_TEXT
        )

    def test_serializer_list(self):
        data = PostSerializer([self.post_1, self.post_2], many=True).data
        expected_data = [
            {
                'id': self.post_1.id,
                'author': AUTHOR,
                'text': POST_1_TEXT,
                'group': self.group.id,
                'image': None
            },
            {
                'id': self.post_2.id,
                'author': AUTHOR,
                'text': POST_2_TEXT,
                'group': None,
                'image': None
            }
        ]
        self.assertEqual(data, expected_data)

    def test_serializer_detail(self):
        data = PostSerializer(self.post_1).data
        expected_data = {
            'id': self.post_1.id,
            'author': AUTHOR,
            'text': POST_1_TEXT,
            'group': self.group.id,
            'image': None
        }
        self.assertEqual(data, expected_data)
