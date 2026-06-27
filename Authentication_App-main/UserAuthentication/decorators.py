"""
Custom decorators for the authentication app.

login_required here wraps Django's own login_required instead of
re-implementing the authentication check (point 8) -- this means it
automatically supports `next=` redirect chaining and honors
settings.LOGIN_URL, while still showing the app's custom flash message.

anonymous_required (point 9) is the inverse: keeps already-logged-in users
from being shown the login/registration forms again.
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required as django_login_required
from django.shortcuts import redirect


def login_required(view_func):
    """
    Require authentication, with a custom flash message, while still
    getting Django's `next=` redirect-back-after-login behaviour for free.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login")
        return django_login_required(view_func)(request, *args, **kwargs)

    return wrapper


def anonymous_required(redirect_to='home'):
    """
    Inverse of login_required: redirect already-authenticated users away
    from views that only make sense for logged-out visitors (login page,
    registration wizard). Usage:

        @anonymous_required()
        def some_view(request): ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_to)
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
