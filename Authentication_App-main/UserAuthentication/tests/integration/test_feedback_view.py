from django.core import mail
from django.test import TestCase
from django.urls import reverse


class FeedbackViewTests(TestCase):
    def setUp(self):
        self.url = reverse('feedback')

    def test_get_renders_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Feedback Form")

    def test_post_sends_email_and_returns_json(self):
        response = self.client.post(self.url, {
            'name': 'Jane Doe',
            'description': 'Great app, one suggestion: dark mode.',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Feedback sent successfully!"})

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Jane Doe", mail.outbox[0].subject)
        self.assertIn("dark mode", mail.outbox[0].body)
