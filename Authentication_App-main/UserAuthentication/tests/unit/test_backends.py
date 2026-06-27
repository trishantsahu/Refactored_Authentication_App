from django.contrib.auth import get_user_model
from django.test import TestCase

from UserAuthentication.backends import MultiFieldAuthBackend

CustomUser = get_user_model()


class MultiFieldAuthBackendTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="janedoe",
            email="janedoe@barc.gov.in",
            password="StrongPassw0rd!2024",
            employee_id="12345",
        )
        cls.backend = MultiFieldAuthBackend()

    def test_authenticate_with_username(self):
        user = self.backend.authenticate(None, username="janedoe", password="StrongPassw0rd!2024")
        self.assertEqual(user, self.user)

    def test_authenticate_with_email(self):
        user = self.backend.authenticate(
            None, username="janedoe@barc.gov.in", password="StrongPassw0rd!2024"
        )
        self.assertEqual(user, self.user)

    def test_authenticate_with_employee_id(self):
        user = self.backend.authenticate(None, username="12345", password="StrongPassw0rd!2024")
        self.assertEqual(user, self.user)

    def test_authenticate_with_wrong_password(self):
        user = self.backend.authenticate(None, username="janedoe", password="wrong-password")
        self.assertIsNone(user)

    def test_authenticate_with_unknown_identifier(self):
        user = self.backend.authenticate(None, username="doesnotexist", password="whatever")
        self.assertIsNone(user)

    def test_authenticate_missing_credentials(self):
        self.assertIsNone(self.backend.authenticate(None, username=None, password="x"))
        self.assertIsNone(self.backend.authenticate(None, username="janedoe", password=None))

    def test_inactive_user_cannot_authenticate(self):
        self.user.is_active = False
        self.user.save()
        user = self.backend.authenticate(None, username="janedoe", password="StrongPassw0rd!2024")
        self.assertIsNone(user)
