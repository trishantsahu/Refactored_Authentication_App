from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse

from UserAuthentication.forms import MultiFieldLoginForm


class CustomLoginView(LoginView):
    """
    Built-in LoginView, paired with MultiFieldLoginForm + the
    MultiFieldAuthBackend authentication backend, so users can log in with
    their username, email, OR employee_id -- without this view needing to
    know anything about that lookup logic itself.
    """

    template_name = 'UserAuthentication/login.html'
    form_class = MultiFieldLoginForm
    redirect_authenticated_user = True  # already-logged-in users skip straight past login

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Login successful!")
        return response

    def get_success_url(self):
        # Honors `?next=` if present (e.g. when login_required redirected
        # the user here), otherwise falls back to LOGIN_REDIRECT_URL.
        return self.get_redirect_url() or str(reverse('home'))
