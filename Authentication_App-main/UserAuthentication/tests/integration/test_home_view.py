from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

CustomUser = get_user_model()


class HomeViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="homeuser",
            password="Tr1cky&UnusualPass!9",
            email="homeuser@barc.gov.in",
            employee_id="66666",
        )
        cls.url = reverse('home')

    def test_anonymous_user_redirected_to_login_with_next(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_authenticated_user_can_view_home(self):
        self.client.login(username='homeuser', password='Tr1cky&UnusualPass!9')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # rendered via the render_page inclusion tag, not hand-duplicated markup
        self.assertContains(response, "Content for Subtab 1 of Page 1")
        self.assertContains(response, "Content for Subtab 1 of Page 2")

    def test_home_response_is_not_cached(self):
        self.client.login(username='homeuser', password='Tr1cky&UnusualPass!9')
        response = self.client.get(self.url)
        self.assertIn('no-cache', response.get('Cache-Control', ''))
