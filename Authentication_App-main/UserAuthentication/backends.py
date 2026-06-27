"""
Custom authentication backend.

CustomUser supports three login identifiers: ``username``, ``email``, and
``employee_id``. Rather than have every view that authenticates a user
(LoginView, admin, future API endpoints, management commands, etc.) repeat
three separate authenticate()/lookup attempts, that logic lives here, once,
as a proper Django authentication backend. Anything that calls
``django.contrib.auth.authenticate()`` automatically benefits from it.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()


class MultiFieldAuthBackend(ModelBackend):
    """Authenticate using username, email, OR employee_id + password."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            user = UserModel.objects.get(
                Q(username__iexact=username)
                | Q(email__iexact=username)
                | Q(employee_id=username)
            )
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            # Defensive: should not happen since username/email/employee_id
            # are all unique fields, but never authenticate ambiguously.
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
