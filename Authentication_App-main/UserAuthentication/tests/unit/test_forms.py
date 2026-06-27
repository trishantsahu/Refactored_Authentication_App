from django.contrib.auth import get_user_model
from django.test import TestCase

from UserAuthentication.forms import (
    CredentialsStepForm,
    MultiFieldLoginForm,
    OTPStepForm,
    RegisterStepForm,
)

CustomUser = get_user_model()


class RegisterStepFormTests(TestCase):
    def test_valid_data(self):
        form = RegisterStepForm(data={
            'employee_id': '12345',
            'email': 'newuser@barc.gov.in',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_non_barc_email(self):
        form = RegisterStepForm(data={
            'employee_id': '12345',
            'email': 'newuser@example.com',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_rejects_non_digit_employee_id(self):
        form = RegisterStepForm(data={
            'employee_id': 'abc12',
            'email': 'newuser@barc.gov.in',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('employee_id', form.errors)

    def test_rejects_wrong_length_employee_id(self):
        form = RegisterStepForm(data={
            'employee_id': '123',
            'email': 'newuser@barc.gov.in',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('employee_id', form.errors)

    def test_rejects_duplicate_employee_id(self):
        CustomUser.objects.create_user(
            username='existing', email='existing@barc.gov.in',
            password='StrongPassw0rd!2024', employee_id='99999',
        )
        form = RegisterStepForm(data={
            'employee_id': '99999',
            'email': 'someoneelse@barc.gov.in',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('employee_id', form.errors)

    def test_rejects_duplicate_email(self):
        CustomUser.objects.create_user(
            username='existing2', email='dup@barc.gov.in',
            password='StrongPassw0rd!2024', employee_id='99998',
        )
        form = RegisterStepForm(data={
            'employee_id': '11111',
            'email': 'dup@barc.gov.in',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class OTPStepFormTests(TestCase):
    def test_valid_six_digit_otp(self):
        form = OTPStepForm(data={'otp': '123456'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_non_digit_otp(self):
        form = OTPStepForm(data={'otp': 'abcdef'})
        self.assertFalse(form.is_valid())

    def test_rejects_wrong_length_otp(self):
        form = OTPStepForm(data={'otp': '123'})
        self.assertFalse(form.is_valid())


class CredentialsStepFormTests(TestCase):
    def test_valid_strong_password(self):
        form = CredentialsStepForm(data={
            'password': 'Tr1cky&UnusualPass!9',
            'confirm_password': 'Tr1cky&UnusualPass!9',
            'first_name': 'Test',
            'last_name': 'User',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_mismatched_passwords(self):
        form = CredentialsStepForm(data={
            'password': 'Tr1cky&UnusualPass!9',
            'confirm_password': 'SomethingElse!9',
            'first_name': 'Test',
            'last_name': 'User',
        })
        self.assertFalse(form.is_valid())

    def test_rejects_weak_password(self):
        """
        Regression test for the validator-bypass fix: a weak password (too
        short, all-numeric) must be rejected by the form itself via
        validate_password(), before it would ever reach
        CustomUser.objects.create_user().
        """
        form = CredentialsStepForm(data={
            'password': '1234567',
            'confirm_password': '1234567',
            'first_name': 'Test',
            'last_name': 'User',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_rejects_common_password(self):
        form = CredentialsStepForm(data={
            'password': 'password123',
            'confirm_password': 'password123',
            'first_name': 'Test',
            'last_name': 'User',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)


class MultiFieldLoginFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username='loginuser', email='loginuser@barc.gov.in',
            password='Tr1cky&UnusualPass!9', employee_id='22222',
        )

    def test_valid_login_with_username(self):
        form = MultiFieldLoginForm(data={'username': 'loginuser', 'password': 'Tr1cky&UnusualPass!9'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_login_wrong_password(self):
        form = MultiFieldLoginForm(data={'username': 'loginuser', 'password': 'wrong'})
        self.assertFalse(form.is_valid())
        self.assertIn('Invalid credentials.', form.errors.get('__all__', []))
