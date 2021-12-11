from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()

INDEX_URL = reverse('posts:index')
SIGNUP_URL = reverse('users:signup')


class UserCreateFormTests(TestCase):
    def setUp(self):
        self.guest = Client()

    def test_create_new_user(self):
        """Валидная форма создания учётной записи
           добавляет в БД нового пользователя."""
        form_data = {
            'first_name': 'Мистер',
            'last_name': 'Твистер',
            'username': 'Twister',
            'email': 'my@email.ru',
            'password1': 'As45OPj9',
            'password2': 'As45OPj9'
        }
        response = self.guest.post(SIGNUP_URL, data=form_data)
        users = User.objects.all()
        self.assertEqual(len(users), 1)
        new_user = users[0]
        self.assertEqual(new_user.first_name, form_data['first_name'])
        self.assertEqual(new_user.last_name, form_data['last_name'])
        self.assertEqual(new_user.username, form_data['username'])
        self.assertEqual(new_user.email, form_data['email'])
        self.assertRedirects(response, INDEX_URL)

    def test_signup_template_shows_correct_context(self):
        """Шаблон signup.html при регистрации нового пользователя
        формируется с правильным контекстом."""
        response = self.guest.get(SIGNUP_URL)
        form_fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2'
        ]
        for field in form_fields:
            self.assertIsInstance(
                response.context['form'].fields[field],
                forms.fields.CharField if field != 'email'
                else forms.fields.EmailField
            )
