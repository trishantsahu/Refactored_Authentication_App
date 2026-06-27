"""
Forms used across the authentication app.

- MultiFieldLoginForm: feeds LoginView, paired with MultiFieldAuthBackend
  (backends.py) so users can sign in with username, email, or employee_id.
- RegisterStepForm / OTPStepForm / CredentialsStepForm: the three steps of
  the registration SessionWizardView (views/registration_wizard.py).
"""

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import (
    validate_password,
    password_validators_help_text_html,
)

from UserAuthentication.services.employee_validation import (
    validate_employee_id_format,
    validate_employee_id_exists,
)

CustomUser = get_user_model()


def validate_barc_email(value):
    if not value.endswith('@barc.gov.in'):
        raise ValidationError('Email must end with @barc.gov.in')


class MultiFieldLoginForm(AuthenticationForm):
    """
    Drop-in replacement for AuthenticationForm's username field, relabelled
    to make clear that username, email, or employee_id are all accepted.
    The actual three-way lookup happens in MultiFieldAuthBackend -- this
    form does not need any custom clean() logic for that part.
    """

    username = forms.CharField(
        label="Username / Email / Employee ID",
        widget=forms.TextInput(attrs={'autofocus': True}),
    )

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': "Invalid credentials.",
        'inactive': "This account is inactive.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        self.fields['username'].widget.attrs.setdefault(
            'placeholder', 'Username or Employee ID or email ID'
        )
        self.fields['password'].widget.attrs.setdefault('placeholder', 'Password')


class _BootstrapFormMixin:
    """Adds the 'form-control' class to every field's widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class RegisterStepForm(_BootstrapFormMixin, forms.Form):
    """Step 1 of the registration wizard: collect + validate employee_id/email."""

    employee_id = forms.CharField(max_length=5, required=True)
    email = forms.EmailField(required=True, validators=[validate_barc_email])

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get("employee_id")

        # Format check first (point 4) -- cheap, local, fails fast.
        validate_employee_id_format(employee_id)

        if CustomUser.objects.filter(employee_id=employee_id).exists():
            raise ValidationError("This employee ID is already in use.")

        # Seam for the future external HR-system lookup. Runs before any
        # OTP is generated/emailed, since this form is validated in the
        # wizard's first step.
        validate_employee_id_exists(employee_id)

        return employee_id

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email


class OTPStepForm(_BootstrapFormMixin, forms.Form):
    """
    Step 2 of the registration wizard.

    This form only validates the *shape* of the OTP (six digits). The actual
    match-against-the-emailed-OTP and expiry checks need access to wizard
    storage, so they are performed in RegistrationWizard.render_next_step()
    rather than here -- a plain Form has no access to wizard state.
    """

    otp = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'one-time-code'}),
    )

    def clean_otp(self):
        otp = self.cleaned_data.get("otp")
        if not otp.isdigit():
            raise ValidationError("OTP must be a 6-digit number.")
        return otp


class CredentialsStepForm(_BootstrapFormMixin, forms.Form):
    """Step 3 of the registration wizard: set password + name."""

    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        help_text=password_validators_help_text_html(),
    )
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=False)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Runs every validator configured in AUTH_PASSWORD_VALIDATORS
        # (settings.py) -- this is the fix for the validator-bypass issue:
        # because this raises ValidationError here, a weak password never
        # reaches CustomUser.objects.create_user() in the first place.
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match. Please try again.")
        return cleaned_data
