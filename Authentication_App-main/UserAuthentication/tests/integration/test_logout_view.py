from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

CustomUser = get_user_model()


class LogoutViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="logoutuser",
            password="Tr1cky&UnusualPass!9",
            email="logoutuser@barc.gov.in",
            employee_id="55555",
        )

    def test_post_logs_out_and_redirects_to_login(self):
        self.client.login(username='logoutuser', password='Tr1cky&UnusualPass!9')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        # session should no longer be authenticated
        home_response = self.client.get(reverse('home'))
        self.assertRedirects(
            home_response, f"{reverse('login')}?next={reverse('home')}"
        )

    def test_get_is_not_allowed(self):
        """
        Modern Django's built-in LogoutView only accepts POST (to prevent
        CSRF logout attacks) -- GET should be rejected with 405.
        """
        self.client.login(username='logoutuser', password='Tr1cky&UnusualPass!9')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 405)
