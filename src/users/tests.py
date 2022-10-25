from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from hasker.mixins import MockAvatarMixin


class UserTest(MockAvatarMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='test',
            password='Test2020',
            email='test@test.me',
            avatar=self.get_mock_avatar()
        )

    def test_registration(self):
        response = self.client.post(reverse('users:register'), {'username': 'test-reg', 'password': 'Test2020'})
        self.assertContains(response, "Обязательное поле.")

        self.client.post(reverse('users:register'), {
            'username': 'testreg',
            'password': 'Test2020',
            'password2': 'Test2020',
            'email': 'test@test.tt',
            'avatar': self.get_mock_avatar()
        })
        new_user = get_user_model().objects.filter(username='testreg').exists()
        self.assertTrue(new_user)

    def test_authenticated(self):
        self.client.post(reverse('users:login'), {'username': 'test', 'password': 'Test2020'})
        response = self.client.get(reverse('users:settings'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('hasker:index_url'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_NOT_authenticated(self):
        response = self.client.get(reverse('users:settings'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        response = self.client.get(reverse('hasker:ask_url'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_change_email(self):
        self.client.post(reverse('users:login'), {'username': 'test', 'password': 'Test2020'})
        user = get_user_model().objects.get(username='test')
        response = self.client.post(reverse('users:settings'), {'email': 'new@email.ru'})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        user.refresh_from_db()
        self.assertEqual(user.email, 'new@email.ru')
