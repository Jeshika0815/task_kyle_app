from unittest.mock import patch, Mock
from django.test import TestCase
from django.urls import reverse


class WelcomeViewTests(TestCase):
    def test_welcome_page_renders(self):
        response = self.client.get(reverse('visitor'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visitor.html')


class LoginViewTests(TestCase):
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


class SigninViewTests(TestCase):
    @patch('home.views.requests.post')
    def test_signin_post_success_sets_session_and_redirects(self, mock_post):
        mock_post.return_value = Mock(status_code=200, json=lambda: {'access_token': 'fake-jwt'})
        response = self.client.post(reverse('signin'), {'email': 'new@example.com', 'password': 'pass1234'})
        self.assertRedirects(response, reverse('home'))

    @patch('home.views.requests.post')
    def test_signin_post_failure_shows_error(self, mock_post):
        mock_post.return_value = Mock(status_code=400)
        response = self.client.post(reverse('signin'), {'email': 'dup@example.com', 'password': 'x'})
        self.assertContains(response, '登録に失敗しました')


class DocsViewTests(TestCase):
    def test_docs_page_renders(self):
        response = self.client.get(reverse('docs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'help.html')


class HomeViewTests(TestCase):
    def test_redirects_to_login_when_no_session_token(self):
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('login'))

    @patch('home.views.requests.get')
    def test_renders_tasks_when_logged_in(self, mock_get):
        session = self.client.session
        session['token'] = 'fake-jwt'
        session.save()
        mock_get.return_value = Mock(status_code=200, json=lambda: [{'plan_name': 'テスト予定'}])

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        called_headers = mock_get.call_args.kwargs['headers']
        self.assertEqual(called_headers['Authorization'], 'Bearer fake-jwt')

    @patch('home.views.requests.get', side_effect=__import__('requests').RequestException('down'))
    def test_shows_error_when_api_unreachable(self, mock_get):
        session = self.client.session
        session['token'] = 'fake-jwt'
        session.save()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)


class DeleteScheduleViewTests(TestCase):
    def test_redirects_to_login_when_no_session_token(self):
        response = self.client.get(reverse('delete', kwargs={'task_id': 1}))
        self.assertRedirects(response, reverse('login'))
