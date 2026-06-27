from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

from UserAuthentication.views.feedback_views import feedback_view
from UserAuthentication.views.home_views import home
from UserAuthentication.views.login_views import CustomLoginView
from UserAuthentication.views.logout_views import CustomLogoutView
from UserAuthentication.views.registration_wizard import RegistrationWizard

urlpatterns = [
    # --- Root -------------------------------------------------------
    # Named view instead of an inline lambda: testable, and shows up
    # properly in `./manage.py show_urls` / admin/debug tooling.
    path('', RedirectView.as_view(pattern_name='login', query_string=True), name='index'),

    # --- Auth: login / logout ---------------------------------------
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # --- Registration pipeline (single wizard: employee_id/email -> OTP -> credentials) ---
    path('register/', RegistrationWizard.as_view(), name='register'),

    # --- Forgot / reset password (Django's built-in, token-based views) ---
    path(
        'forgot_password/',
        auth_views.PasswordResetView.as_view(
            template_name='UserAuthentication/forgot_password.html',
            email_template_name='UserAuthentication/password_reset_email.txt',
            subject_template_name='UserAuthentication/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
        ),
        name='forgot_password',
    ),
    path(
        'forgot_password/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='UserAuthentication/forgot_password_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reset_password/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='UserAuthentication/reset_password.html',
            success_url=reverse_lazy('login'),
        ),
        name='reset_password',
    ),

    # --- Feedback -----------------------------------------------------
    path('feedback/', feedback_view, name='feedback'),

    # --- Home -----------------------------------------------------------
    path('home/', home, name='home'),
]
