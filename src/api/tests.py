from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from hasker.models import Answer, Question, Tag
from users.test.mocks import MockAvatarMixin


class ApiTest(MockAvatarMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='test',
            password='Test2020',
            email='test@test.me',
            avatar=self.get_mock_avatar()
        )
        self.question = Question.objects.create(
            title='заголовок вопроса',
            text='текст вопроса',
            author=self.user,
        )
        Tag.objects.create(name='www')
        Tag.objects.create(name='http')
        Answer.objects.create(
            text='текст ответа',
            author=self.user,
            question=self.question,
        )
        self.client.post(reverse('users:login'), {'username': 'test', 'password': 'Test2020'})

    def test_search(self):
        response = self.client.get(f"{reverse('api:search-list')}?q=текст вопроса")
        results = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['text'], 'текст вопроса')

        response = self.client.get(f"{reverse('api:search-list')}?q=заголовок вопроса")
        results = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results[0]['title'], 'заголовок вопроса')

        self.client.post(reverse('hasker:ask_url'), {'title': 'Мой вопрос', 'text': 'содержание', 'question_tags': 'www, lll'})
        response = self.client.get(f"{reverse('api:search-list')}?q=tag:www")
        results = response.json()
        self.assertEqual(results[0]['title'], 'Мой вопрос')

    def test_questions(self):
        mock_result = {'id': 1, 'author': 'test', 'rating': 0, 'title': 'заголовок вопроса', 'text': 'текст вопроса'}
        r = self.client.get(reverse('api:questions-list'))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        results = r.json()['results']
        self.assertIsInstance(results, list)
        del results[0]['created_date']
        self.assertEqual(results[0], mock_result)

        r = self.client.get(reverse('api:questions-detail', kwargs={'pk': 1}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        results = r.json()
        del results['created_date']
        self.assertIsInstance(results, dict)
        self.assertEqual(results, mock_result)

    def test_trending(self):
        self.client.post(reverse('hasker:question_rating_url', kwargs={'id': self.question.id}), {'like': 'neg'})

        r = self.client.get(reverse('api:trending-list'))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.json(), {'count': 1, 'next': None, 'previous': None, 'results': [
            {'title': 'заголовок вопроса', 'rating': -1}]})
