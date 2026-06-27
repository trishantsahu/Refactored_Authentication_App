from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

CustomUser = get_user_model()


class LoginViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="testuser",
            password="Tr1cky&UnusualPass!9",
            email="testuser@barc.gov.in",
            employee_id="12345",
        )
        cls.url = reverse('login')

    def test_valid_login_with_username(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'Tr1cky&UnusualPass!9',
        })
        self.assertRedirects(response, reverse('home'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Login successful!")

    def test_valid_login_with_email(self):
        response = self.client.post(self.url, {
            'username': 'testuser@barc.gov.in',
            'password': 'Tr1cky&UnusualPass!9',
        })
        self.assertRedirects(response, reverse('home'))

    def test_valid_login_with_employee_id(self):
        response = self.client.post(self.url, {
            'username': '12345',
            'password': 'Tr1cky&UnusualPass!9',
        })
        self.assertRedirects(response, reverse('home'))

    def test_invalid_login_wrong_password(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid credentials.")

    def test_invalid_login_unknown_identifier(self):
        response = self.client.post(self.url, {
            'username': 'nobody-here',
            'password': 'Tr1cky&UnusualPass!9',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid credentials.")

    def test_already_authenticated_user_skips_login_page(self):
        self.client.login(username='testuser', password='Tr1cky&UnusualPass!9')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home'))

    def test_login_requires_csrf_token_when_enforced(self):
        strict_client = Client(enforce_csrf_checks=True)
        response = strict_client.post(self.url, {
            'username': 'testuser',
            'password': 'Tr1cky&UnusualPass!9',
        })
        self.assertEqual(response.status_code, 403)
