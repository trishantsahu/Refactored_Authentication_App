from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy


class CustomLogoutView(LogoutView):
    """
    Built-in LogoutView already calls request.session.flush() (which both
    clears session data AND rotates the session key -- stronger than the
    old view's plain request.session.clear()) before logging the user out.
    """

    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, "Logged out successfully!")
        return response
