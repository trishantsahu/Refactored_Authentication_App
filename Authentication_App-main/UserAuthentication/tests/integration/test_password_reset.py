import re

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

CustomUser = get_user_model()


class PasswordResetFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="resetuser",
            password="OldPassw0rd!9",
            email="resetuser@barc.gov.in",
            employee_id="77777",
        )

    def test_forgot_password_sends_email_with_working_link(self):
        response = self.client.post(reverse('forgot_password'), {'email': 'resetuser@barc.gov.in'})
        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)

        match = re.search(r'(https?://[^\s]+/reset_password/[^\s]+/[^\s]+/)', mail.outbox[0].body)
        self.assertIsNotNone(match, "Reset link not found in email body")

    def test_forgot_password_does_not_error_for_unknown_email(self):
        """
        Matches Django's secure-by-default behaviour: never reveal whether
        an email address has an account.
        """
        response = self.client.post(reverse('forgot_password'), {'email': 'nobody@barc.gov.in'})
        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_password_with_valid_token_changes_password(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse('reset_password', kwargs={'uidb64': uid, 'token': token})

        # PasswordResetConfirmView redirects from the tokenized URL to a
        # "set-password" session-based URL on first GET; follow it.
        get_response = self.client.get(url, follow=True)
        self.assertEqual(get_response.status_code, 200)

        final_url = get_response.redirect_chain[-1][0] if get_response.redirect_chain else url
        post_response = self.client.post(final_url, {
            'new_password1': 'BrandNewStrongPass!42',
            'new_password2': 'BrandNewStrongPass!42',
        })
        self.assertRedirects(post_response, reverse('login'))

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('BrandNewStrongPass!42'))
        self.assertFalse(self.user.check_password('OldPassw0rd!9'))

    def test_reset_password_with_invalid_token_shows_invalid_link(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse('reset_password', kwargs={'uidb64': uid, 'token': 'bogus-token'})
        response = self.client.get(url, follow=True)
        self.assertContains(response, "invalid or has already been used")

    def test_token_is_invalidated_after_password_change(self):
        """
        Core advantage of PasswordResetTokenGenerator over the old
        session-stored random token: the token is derived from the
        password hash, so it stops working the moment the password
        changes -- it can't be reused.
        """
        token = default_token_generator.make_token(self.user)
        self.user.set_password('SomeOtherPassword!1')
        self.user.save()
        self.assertFalse(default_token_generator.check_token(self.user, token))
