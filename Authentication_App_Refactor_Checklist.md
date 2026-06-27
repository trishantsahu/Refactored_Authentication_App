# Authentication_App Refactor — Checklist

A full record of everything discussed, what was actually implemented in the
refactored zip, and what was deliberately left alone.

## 1. URL Routing
- [x] Replaced inline `lambda` root redirect with a named `RedirectView` (`index`)
- [x] Grouped URLs by lifecycle stage in `urls.py` (auth / registration / password-reset / feedback / home)
- [ ] App namespacing (`app_name` + `include(..., namespace=...)`) — discussed, not applied (would require updating every `{% url %}` call; left as a future option since this is a single-app project today)

## 2. Multi-Credential Login (username / email / employee_id)
- [x] Created `UserAuthentication/backends.py` → `MultiFieldAuthBackend`
- [x] Registered it in `AUTHENTICATION_BACKENDS` (with `ModelBackend` kept as fallback)
- [x] Old 3x sequential `authenticate()` calls in the login view removed — now a single `authenticate()` call resolves all three identifiers

## 3. Class-Based Views
- [x] `CustomLoginView` (subclasses `LoginView`) with `MultiFieldLoginForm`, `redirect_authenticated_user=True`
- [x] `CustomLogoutView` (subclasses `LogoutView`) with custom flash message
- [x] `PasswordResetView` / `PasswordResetDoneView` / `PasswordResetConfirmView` (built-in, see §14)
- [x] Registration converted to `django-formtools`' `SessionWizardView` (`RegistrationWizard`) — replaces the old `register_views.py` / `otp_views.py` / `credential_views.py` trio
- [x] Manual `request.session['otp']` / `['email']` / `['employee_id']` / `['otp_verified']` bookkeeping removed — wizard's own session-backed storage replaces it

## 4. Employee ID Validation (future external lookup)
- [x] Created `UserAuthentication/services/employee_validation.py`
- [x] `validate_employee_id_format()` — actually enforced now, via `RegisterStepForm.clean_employee_id()`
- [x] `validate_employee_id_exists()` — placeholder seam added, runs **before** OTP is generated/emailed, ready for the future external HR-system integration

## 5 & 6. Password Strength Validation
- [x] `CredentialsStepForm.clean_password()` calls Django's `validate_password()` against `AUTH_PASSWORD_VALIDATORS`
- [x] `password_validators_help_text_html()` wired in as field help text (auto-generated "suggestions")
- [x] **Bug fix**: closes the validator-bypass — weak passwords now rejected by the form before `create_user()` is ever called
- [ ] Client-side live strength meter (e.g. `zxcvbn`) — discussed as a nice-to-have, not implemented

## 7. Sessions vs JWT/DRF
- [x] Explained the tradeoff; confirmed sessions are the right fit for this server-rendered app
- [ ] No code change — kept session-based auth as-is (by design, not an oversight)

## 8 & 9. Decorators
- [x] `login_required` rewritten to delegate to Django's built-in `login_required` (gets `next=` redirect chaining + `LOGIN_URL` support for free) while keeping the custom flash message
- [x] `anonymous_required` added (keeps logged-in users off `/login/` and the registration wizard)
- [x] `@never_cache` applied to the `home` view
- [x] `@require_http_methods` applied to the `feedback` view
- [ ] `@sensitive_post_parameters` — discussed, not added in this pass
- [ ] Rate limiting (`django-ratelimit`) on login/forgot-password/OTP — discussed as a recommendation, not implemented (extra dependency, left as future work)

## 10. `my_tags.py` Template Tag
- [x] Converted `render_page` from a `simple_tag` (raw f-string HTML, no autoescaping) to an `inclusion_tag`
- [x] Markup moved to a real template: `templates/UserAuthentication/partials/_tab_widget.html`
- [x] `home.html` updated to actually call `{% render_page %}` (previously the tag existed but was unused — `home.html` had the markup hand-duplicated instead)

## 11–13. Explicitly Skipped (per instruction)
- [ ] Removing/rotating the hardcoded credentials & token in `settings.py` — **left untouched**
- [ ] Deleting the stale root `UserAuthentication/views.py` stub — **left untouched** (confirmed harmless: Python's import system resolves the `views/` package before a same-named sibling module, so it's never actually imported)

## 14. Password Reset Flow
- [x] Replaced hand-rolled `get_random_string(20)` + session-stored token with Django's `PasswordResetTokenGenerator`
- [x] `PasswordResetView` / `PasswordResetDoneView` / `PasswordResetConfirmView` wired into `urls.py`
- [x] `password_reset_subject.txt` / `password_reset_email.txt` templates added
- [x] `reset_password.html` rewritten for `SetPasswordForm` (`new_password1`/`new_password2`) + `validlink` handling
- [x] Token now self-expires and self-invalidates on password change (vs. no expiry check at all previously)

## Bugs Found & Fixed During the Refactor (not explicitly requested, found while building)
- [x] `login(self.request, user)` after `create_user()` would raise `ValueError` — multiple `AUTHENTICATION_BACKENDS` are configured, so an explicit `backend=` argument is now passed
- [x] `feedback_view`'s `send_mail()` used `settings.EMAIL_HOST_USER`, which is unset under the console email backend — switched to `settings.DEFAULT_FROM_EMAIL`
- [x] Logout link converted from a `GET` `<a href>` to a `POST` `<form>` — Django 4.1+'s `LogoutView` only accepts `POST`
- [x] Removed dead static files (`register.js`, `otp_verification.js`, `register.css`, `otp_verification.css`) that referenced the deleted views, and the now-broken `{% static 'UserAuthentication/js/register.js' %}` reference in `base_generic.html`

## Project Hygiene
- [x] `requirements.txt` added (`Django`, `django-formtools`)
- [x] `README.md` added — setup steps, what changed, what was deliberately skipped, and an honest note on test execution limits in the build sandbox
- [x] Full test suite added/rewritten to match the new flow: `tests/unit/`, `tests/integration/`, `tests/e2e/` (backends, forms, decorators, login/logout/home/feedback, full password-reset flow, full registration wizard happy-path + failure modes)
