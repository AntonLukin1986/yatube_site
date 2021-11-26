from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserCreateFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_new_user(self):
        """Заполненная форма создания учётной записи
           добавляет нового пользователя в модель User."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Мистер',
            'last_name': 'Твистер',
            'username': 'Twister',
            'email': 'my@email.ru',
            'password1': 'As45OPj9',
            'password2': 'As45OPj9'
        }
        self.guest_client.post(reverse('users:signup'), data=form_data)
        self.assertEqual(User.objects.count(), users_count + 1)
