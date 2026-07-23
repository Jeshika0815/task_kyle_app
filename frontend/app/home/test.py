from unittest.mock import patch, Mock
# This project has no local database (it only talks to the FastAPI backend),
# so SimpleTestCase is used instead of TestCase to avoid DB setup/teardown.
from django.test import SimpleTestCase
from django.urls import reverse


class WelcomeViewTests(SimpleTestCase):
    def test_welcome_page_renders(self):
        response = self.client.get(reverse('visitor'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visitor.html')


class LoginViewTests(SimpleTestCase):
    def test_login_get_renders_form(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    @patch('home.views.requests.post')
    def test_login_post_success_sets_session_and_redirects(self, mock_post):
        mock_post.return_value = Mock(status_code=200, json=lambda: {'access_token': 'fake-jwt'})
        response = self.client.post(reverse('login'), {'email': 'a@example.com', 'password': 'pass1234'})
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(self.client.session['token'], 'fake-jwt')

    @patch('home.views.requests.post')
    def test_login_post_failure_shows_error(self, mock_post):
        mock_post.return_value = Mock(status_code=401)
        response = self.client.post(reverse('login'), {'email': 'a@example.com', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ログインに失敗しました')


class GoogleCallbackViewTests(SimpleTestCase):
    @patch('home.views.requests.get')
    def test_callback_with_code_sets_session_and_redirects(self, mock_get):
        mock_get.return_value = Mock(status_code=200, json=lambda: {'access_token': 'fake-jwt'})
        response = self.client.get(reverse('google_callback'), {'code': 'abc123'})
        # fetch_redirect_response=False: /dashboard/ itself calls requests.get
        # too, and this single mock isn't shaped for that follow-up call.
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)
        self.assertEqual(self.client.session['token'], 'fake-jwt')
        called_params = mock_get.call_args.kwargs['params']
        self.assertEqual(called_params['code'], 'abc123')

    def test_callback_without_code_shows_error(self):
        response = self.client.get(reverse('google_callback'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'キャンセル')

    @patch('home.views.requests.get')
    def test_callback_exchange_failure_shows_error(self, mock_get):
        mock_get.return_value = Mock(status_code=400)
        response = self.client.get(reverse('google_callback'), {'code': 'bad'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Google認証に失敗しました')


class SigninViewTests(SimpleTestCase):
    @patch('home.views.requests.post')
    def test_signin_post_success_logs_in_and_redirects(self, mock_post):
        # First call is /auth/register, second is the follow-up /auth/login
        # (register doesn't issue a token by itself).
        mock_post.side_effect = [
            Mock(status_code=200, json=lambda: {'id': 1, 'email': 'new@example.com'}),
            Mock(status_code=200, json=lambda: {'access_token': 'fake-jwt'}),
        ]
        response = self.client.post(reverse('signin'), {'email': 'new@example.com', 'password': 'pass1234'})
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(self.client.session['token'], 'fake-jwt')

    @patch('home.views.requests.post')
    def test_signin_post_failure_shows_error(self, mock_post):
        mock_post.return_value = Mock(status_code=400)
        response = self.client.post(reverse('signin'), {'email': 'dup@example.com', 'password': 'x'})
        self.assertContains(response, '登録に失敗しました')


class DocsViewTests(SimpleTestCase):
    def test_docs_page_renders(self):
        response = self.client.get(reverse('docs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'help.html')


class HomeViewTests(SimpleTestCase):
    def _login(self):
        # SESSION_ENGINE is signed_cookies (this project has no local database),
        # so a session token can only be set through a real request/response
        # round trip - poking self.client.session directly doesn't persist it.
        with patch('home.views.requests.post') as mock_post:
            mock_post.return_value = Mock(status_code=200, json=lambda: {'access_token': 'fake-jwt'})
            self.client.post(reverse('login'), {'email': 'a@example.com', 'password': 'pass1234'})

    def test_redirects_to_login_when_no_session_token(self):
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('login'))

    @patch('home.views.requests.get')
    def test_renders_tasks_when_logged_in(self, mock_get):
        self._login()
        mock_get.return_value = Mock(status_code=200, json=lambda: [{
            'id': 1, 'plan_name': 'テスト予定',
            'date': {'start_date': None, 'finish_date': None},
            'time': {'start_time': None, 'finish_time': None},
            'alarm': False, 'repeats': None, 'tags': [], 'location': None,
            'url': None, 'memo': None, 'departure': None,
        }])

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        called_headers = mock_get.call_args.kwargs['headers']
        self.assertEqual(called_headers['Authorization'], 'Bearer fake-jwt')
        self.assertContains(response, 'テスト予定')

    @patch('home.views.requests.get', side_effect=__import__('requests').RequestException('down'))
    def test_shows_error_when_api_unreachable(self, mock_get):
        self._login()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)


class DeleteScheduleViewTests(SimpleTestCase):
    def test_redirects_to_login_when_no_session_token(self):
        response = self.client.get(reverse('delete', args=[1]))
        self.assertRedirects(response, reverse('login'))
