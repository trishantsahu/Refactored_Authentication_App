"""
Registration pipeline implemented as a formtools SessionWizardView.

Replaces the old hand-rolled register_views.py / otp_views.py /
credential_views.py trio. Per-step data (employee_id, email, OTP, password,
name) now lives in the wizard's own session-backed storage instead of being
manually poked into request.session under ad-hoc keys -- and the wizard
structurally refuses to render step N+1 until step N has validated, which is
what the old @otp_verification_mail_sent / @otp_verified decorators existed
to enforce by hand.
"""

import random
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.utils import timezone

from formtools.wizard.views import SessionWizardView

from UserAuthentication.forms import CredentialsStepForm, OTPStepForm, RegisterStepForm

CustomUser = get_user_model()

OTP_EXPIRY_MINUTES = getattr(settings, 'OTP_EXPIRY_MINUTES', 7)

REGISTER_STEP = 'register'
OTP_STEP = 'otp'
CREDENTIALS_STEP = 'credentials'


class RegistrationWizard(SessionWizardView):
    template_name = 'UserAuthentication/registration_wizard.html'

    form_list = [
        (REGISTER_STEP, RegisterStepForm),
        (OTP_STEP, OTPStepForm),
        (CREDENTIALS_STEP, CredentialsStepForm),
    ]

    def dispatch(self, request, *args, **kwargs):
        # CBV equivalent of @anonymous_required: the decorator in
        # decorators.py is written for function-based views (request as the
        # first positional arg) and doesn't bind correctly when applied
        # directly to a class method's `dispatch(self, request, ...)`
        # signature, so the check is inlined here instead.
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    # ------------------------------------------------------------------
    # Step-specific hooks
    # ------------------------------------------------------------------

    def process_step(self, form):
        """
        Runs right after the *current* step's form has validated, before
        the wizard advances. Used here to generate + email the OTP exactly
        once, right after the register step succeeds.
        """
        if self.steps.current == REGISTER_STEP:
            otp = f"{random.randint(0, 999999):06d}"
            self.storage.extra_data['otp'] = otp
            self.storage.extra_data['otp_generated_at'] = timezone.now().isoformat()

            email = form.cleaned_data['email']
            send_mail(
                'Your OTP for verification',
                f'Your OTP is {otp}. It will expire in {OTP_EXPIRY_MINUTES} minutes.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        return self.get_form_step_data(form)

    def render_next_step(self, form, **kwargs):
        """
        Intercepts the transition out of the OTP step to check the entered
        OTP against the one generated in process_step(), including expiry.
        A plain form.clean() can't do this because it has no access to
        wizard storage -- this is the wizard-level equivalent of the old
        verify_otp view.
        """
        if self.steps.current == OTP_STEP:
            entered_otp = form.cleaned_data['otp']
            expected_otp = self.storage.extra_data.get('otp')
            generated_at_raw = self.storage.extra_data.get('otp_generated_at')

            expired = True
            if generated_at_raw:
                generated_at = timezone.datetime.fromisoformat(generated_at_raw)
                expired = timezone.now() - generated_at > timedelta(minutes=OTP_EXPIRY_MINUTES)

            if expired:
                messages.error(self.request, "OTP has expired. Please restart registration.")
                self.storage.reset()
                return redirect('register')

            if entered_otp != expected_otp:
                messages.error(self.request, "Invalid OTP, please try again.")
                return self.render(form)

        return super().render_next_step(form, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == OTP_STEP:
            context['otp_generated_at'] = self.storage.extra_data.get('otp_generated_at')
            context['otp_expiry_minutes'] = OTP_EXPIRY_MINUTES
        return context

    # ------------------------------------------------------------------
    # Final step
    # ------------------------------------------------------------------

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        username = data['email'].split('@')[0]

        user = CustomUser.objects.create_user(
            username=username,
            email=data['email'],
            password=data['password'],  # already passed validate_password() in CredentialsStepForm
            first_name=data['first_name'],
            last_name=data.get('last_name', ''),
            employee_id=data['employee_id'],
        )

        send_mail(
            f"[DSL] Account created successfully for {data['first_name']}",
            (
                f"You can log in using your email ({data['email']}), "
                f"employee ID ({data['employee_id']}), or username ({username}).\n\n"
                "This is an auto-generated mail from the system. Please do not respond to this mail.\n\n"
                "Regards\nROD\nBARC"
            ),
            settings.DEFAULT_FROM_EMAIL,
            [data['email']],
            fail_silently=False,
        )

        login(self.request, user, backend='UserAuthentication.backends.MultiFieldAuthBackend')
        messages.success(self.request, "Registration successful! You are now logged in.")
        return redirect('home')
