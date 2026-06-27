import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

CustomUser = get_user_model()

WIZARD_PREFIX = 'registration_wizard'  # formtools' normalize_name("RegistrationWizard")


def _extract_otp(email_body):
    match = re.search(r'Your OTP is (\d{6})', email_body)
    assert match, f"Could not find OTP in email body: {email_body!r}"
    return match.group(1)


class RegistrationWizardHappyPathTests(TestCase):
    def setUp(self):
        self.url = reverse('register')

    def test_full_registration_flow_creates_and_logs_in_user(self):
        # --- Step 1: register (employee_id + email) -----------------
        response = self.client.post(self.url, {
            f'{WIZARD_PREFIX}-current_step': 'register',
            'register-employee_id': '54321',
            'register-email': 'wizarduser@barc.gov.in',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Verify Your OTP")
        self.assertEqual(len(mail.outbox), 1)
        otp = _extract_otp(mail.outbox[0].body)

        # --- Step 2: OTP ---------------------------------------------
        response = self.client.post(self.url, {
            f'{WIZARD_PREFIX}-current_step': 'otp',
            'otp-otp': otp,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Your Credentials")

        # --- Step 3: credentials --------------------------------------
        response = self.client.post(self.url, {
            f'{WIZARD_PREFIX}-current_step': 'credentials',
            'credentials-password': 'Tr1cky&UnusualPass!9',
            'credentials-confirm_password': 'Tr1cky&UnusualPass!9',
            'credentials-first_name': 'Wizard',
            'credentials-last_name': 'User',
        })
        self.assertRedirects(response, reverse('home'))

        # User was actually created with the right fields.
        user = CustomUser.objects.get(email='wizarduser@barc.gov.in')
        self.assertEqual(user.employee_id, '54321')
        self.assertEqual(user.username, 'wizarduser')
        self.assertTrue(user.check_password('Tr1cky&UnusualPass!9'))

        # Account-created confirmation email was sent (2nd outbox entry).
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn('wizarduser@barc.gov.in', mail.outbox[1].body)

        # User is auto-logged-in: home page should now be reachable.
        home_response = self.client.get(reverse('home'))
        self.assertEqual(home_response.status_code, 200)


class RegistrationWizardValidationTests(TestCase):
    def setUp(self):
        self.url = reverse('register')

    def test_duplicate_employee_id_rejected_at_step_one(self):
        CustomUser.objects.create_user(
            username='existing', email='existing@barc.gov.in',
            password='Tr1cky&UnusualPass!9', employee_id='10000',
        )
        response = self.client.post(self.url, {
            f'{WIZARD_PREFIX}-current_step': 'register',
            'register-employee_id': '10000',
            'register-email': 'another@barc.gov.in',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This employee ID is already in use.")
        # Should not have advanced past step 1, so no OTP email yet.
        self.assertEqual(len(mail.outbox), 0)

    def test_non_barc_email_rejected_at_step_one(self):
        response = self.client.post(self.url, {
            f'{WIZARD_PREFIX}-current_step': 'register',
            'register-employee_id': '10001',
            'register-email': 'someone@gmail.com',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email must end with @barc.gov.in")

    def test_invalid_otp_is_rejected_and_step_does_not_advance(self):
        response = self.client.post(self.url, {
            f'{WIZARD_PREFIX}-current_step': 'register',
            'register-employee_id': '10002',
            'register-email': 'otptest@barc.gov.in',
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.url, {
            f'{WIZARD_PREFIX}-current_step': 'otp',
            'otp-otp': '000000',  # wrong on purpose
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid OTP, please try again.")
        # Still on the OTP step, not advanced to credentials.
        self.assertContains(response, "Verify Your OTP")

    def test_weak_password_rejected_at_credentials_step(self):
        response = self.client.post(self.url, {
            f'{WIZARD_PREFIX}-current_step': 'register',
            'register-employee_id': '10003',
            'register-email': 'weakpass@barc.gov.in',
        })
        otp = _extract_otp(mail.outbox[0].body)

        response = self.client.post(self.url, {
            f'{WIZARD_PREFIX}-current_step': 'otp',
            'otp-otp': otp,
        })
        self.assertContains(response, "Create Your Credentials")

        response = self.client.post(self.url, {
            f'{WIZARD_PREFIX}-current_step': 'credentials',
            'credentials-password': '1234567',
            'credentials-confirm_password': '1234567',
            'credentials-first_name': 'Weak',
            'credentials-last_name': 'Pass',
        })
        # Should be re-rendered (still 200), not redirected to home, and no
        # user should have been created with this weak password.
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(email='weakpass@barc.gov.in').exists())

    def test_anonymous_required_redirects_logged_in_user_away_from_registration(self):
        user = CustomUser.objects.create_user(
            username='alreadyin', email='alreadyin@barc.gov.in',
            password='Tr1cky&UnusualPass!9', employee_id='10004',
        )
        self.client.login(username='alreadyin', password='Tr1cky&UnusualPass!9')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home'))
