import base64
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import Client, TestCase


class UserTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='test',
            password='Test2020',
            email='test@test.me',
            avatar=self.get_mock_avatar()
        )

    @staticmethod
    def get_mock_avatar():
        avatar_base64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQIC' \
                        'AgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vu' \
                        'PBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kov' \
                        'IHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtj' \
                        'W0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XY' \
                        'K1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU' \
                        '+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YI' \
                        'oePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scq' \
                        'OMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3p' \
                        'TImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/' \
                        'N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba' \
                        '2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHr' \
                        'wBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As0' \
                        '8fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprt' \
                        'CohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII='
        img_data = avatar_base64.split(',', maxsplit=1)[1]
        return ContentFile(base64.decodestring(img_data.encode()), name='temp.jpeg')

    def test_registration(self):
        response = self.client.post('/user/register/', {'username': 'test-reg', 'password': 'Test2020'})
        self.assertContains(response, "Обязательное поле.")

        response = self.client.post('/user/register/', {
            'username': 'testreg',
            'password': 'Test2020',
            'password2': 'Test2020',
            'email': 'test@test.tt',
            'avatar': self.get_mock_avatar()
        })
        self.assertContains(response, "Регистрация завершена!")

    def test_authenticated(self):
        self.client.post('/user/login/', {'username': 'test', 'password': 'Test2020'})
        response = self.client.get("/user/settings/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_NOT_authenticated(self):
        response = self.client.get("/user/settings/")
        self.assertEqual(response.status_code, 302)

        response = self.client.get("/ask/")
        self.assertEqual(response.status_code, 302)

    def test_change_email(self):
        self.client.post('/user/login/', {'username': 'test', 'password': 'Test2020'})
        response = self.client.post('/user/settings/', {'email': 'new@email.ru'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user_model().objects.get(username='test').email, 'new@email.ru')
