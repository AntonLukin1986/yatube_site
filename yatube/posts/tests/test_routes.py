from django.test import TestCase
from django.urls import reverse

AUTHOR = 'Author'
POST_ID = 1
SLUG = 'test-slug'


class RoutesURLTest(TestCase):
    def test_named_paths_match_with_explicit_urls(self):
        """Именованные пути совпадают с фактическими URL адресами."""
        cases = [
            ['index', [], '/'],
            ['group_list', [SLUG], f'/group/{SLUG}/'],
            ['profile', [AUTHOR], f'/profile/{AUTHOR}/'],
            ['post_create', [], '/create/'],
            ['post_detail', [POST_ID], f'/posts/{POST_ID}/'],
            ['post_edit', [POST_ID], f'/posts/{POST_ID}/edit/'],
            ['add_comment', [POST_ID], f'/posts/{POST_ID}/comment/'],
            ['follow_index', [], '/follow/'],
            ['profile_follow',
             [AUTHOR],
             f'/profile/{AUTHOR}/follow/'],
            ['profile_unfollow',
             [AUTHOR],
             f'/profile/{AUTHOR}/unfollow/'],
            ['groups_index', [], '/groups/'],
            ['authors_index', [], '/authors/'],
            ['add_like', [POST_ID], f'/posts/{POST_ID}/like/'],
            ['delete_like', [POST_ID], f'/posts/{POST_ID}/unlike/'],
        ]
        for name, param, url in cases:
            with self.subTest(name=name):
                self.assertEqual(reverse(f'posts:{name}', args=param), url)
