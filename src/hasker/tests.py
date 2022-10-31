
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from hasker.models import Answer, Question, Tag
from users.test.mocks import MockAvatarMixin


class EmailTest(MockAvatarMixin, TestCase):
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

    def test_index_page(self):
        response = self.client.get(reverse('hasker:index_url'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "заголовок вопроса")

    def testMail(self):
        self.assertEqual(len(mail.outbox), 1)

    def testMailSubject(self):
        self.assertEqual(mail.outbox[0].subject, 'Answer on your question')

    def test_ask(self):
        response = self.client.get(reverse('hasker:ask_url'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse('hasker:ask_url'), {'title': 'Мой вопрос', 'text': 'содержание', 'question_tags': 'fff, lll'})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn('lll', Tag.objects.all().values_list('name', flat=True))
        response = self.client.get(reverse('hasker:index_url'))
        self.assertContains(response, "Мой вопрос")

        response = self.client.post(reverse('hasker:ask_url'), {'title': 'Мой вопрос'})
        self.assertContains(response, "Обязательное поле")

    def test_tag(self):
        response = self.client.get(f'{reverse("hasker:tag_url")}?q=текст вопроса')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "текст вопроса")

        response = self.client.get(f'{reverse("hasker:tag_url")}?q=заголовок вопроса')
        self.assertContains(response, "заголовок вопроса")

        self.client.post(reverse('hasker:ask_url'), {'title': 'Мой вопрос', 'text': 'содержание', 'question_tags': 'fff, lll'})
        response = self.client.get(f'{reverse("hasker:tag_url")}?q=tag:fff')
        self.assertContains(response, "Мой вопрос")

    def test_answer(self):
        response = self.client.get(reverse("hasker:answer_url", kwargs={'id': self.question.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "текст ответа")

        response = self.client.post(reverse("hasker:answer_url", kwargs={'id': self.question.id}), {'answer': 'годный ответ'})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        response = self.client.get(reverse("hasker:answer_url", kwargs={'id': self.question.id}))
        self.assertContains(response, "годный ответ")

    def test_set_correct(self):
        answer = self.question.answers.all()[0]
        self.assertEqual(answer.is_correct_answer, False)

        self.client.post(reverse("hasker:set_correct_url", kwargs={'id': answer.id}))

        answer = self.question.answers.all()[0]
        self.assertTrue(answer.is_correct_answer)

    def test_answer_rating(self):
        answer = self.question.answers.all()[0]
        self.assertEqual(answer.rating, 0)

        self.client.post(reverse("hasker:answer_rating_url", kwargs={'id': answer.id}), {'like': 'poz'})
        self.client.post(reverse("hasker:answer_rating_url", kwargs={'id': answer.id}), {'like': 'poz'})

        answer = self.question.answers.all()[0]
        self.assertEqual(answer.rating, 1)

        self.client.post(reverse("hasker:answer_rating_url", kwargs={'id': answer.id}), {'like': 'neg'})
        self.client.post(reverse("hasker:answer_rating_url", kwargs={'id': answer.id}), {'like': 'neg'})
        self.client.post(reverse("hasker:answer_rating_url", kwargs={'id': answer.id}), {'like': 'neg'})

        answer = self.question.answers.all()[0]
        self.assertEqual(answer.rating, -1)

    def test_question_rating(self):
        self.assertEqual(self.question.rating, 0)

        self.client.post(reverse("hasker:question_rating_url", kwargs={'id': self.question.id}), {'like': 'neg'})
        self.client.post(reverse("hasker:question_rating_url", kwargs={'id': self.question.id}), {'like': 'neg'})
        self.client.post(reverse("hasker:question_rating_url", kwargs={'id': self.question.id}), {'like': 'neg'})

        question = Question.objects.all()[0]
        self.assertEqual(question.rating, -1)

        self.client.post(reverse("hasker:question_rating_url", kwargs={'id': self.question.id}), {'like': 'poz'})
        self.client.post(reverse("hasker:question_rating_url", kwargs={'id': self.question.id}), {'like': 'poz'})

        question = Question.objects.all()[0]
        self.assertEqual(question.rating, 1)
