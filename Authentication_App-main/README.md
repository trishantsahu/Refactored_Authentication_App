# Authentication_App — Refactored

This is a refactor of the original project, applying the optimizations discussed:

- **Routing**: named `index` redirect instead of an inline lambda; URLs grouped by
  lifecycle stage (auth / registration / password-reset / feedback / home).
- **Multi-credential login**: `UserAuthentication/backends.py` (`MultiFieldAuthBackend`)
  resolves username/email/employee_id once, for any code path that calls `authenticate()`.
- **Class-based views**: `CustomLoginView` / `CustomLogoutView` wrap Django's built-in
  `LoginView`/`LogoutView`. Registration is now a `django-formtools` `SessionWizardView`
  (`UserAuthentication/views/registration_wizard.py`) instead of three separate
  function views manually juggling `request.session`.
- **Employee ID validation**: `UserAuthentication/services/employee_validation.py` —
  format-checked now, with `validate_employee_id_exists()` as the seam for the future
  external HR-system lookup, called before the OTP step.
- **Password strength**: `CredentialsStepForm.clean_password()` calls Django's
  `validate_password()`, so `AUTH_PASSWORD_VALIDATORS` is actually enforced before
  `create_user()` is ever called (fixes the validator-bypass bug).
- **Decorators**: `login_required` now delegates to Django's built-in decorator (gets
  `next=` redirect chaining for free) while keeping the custom flash message;
  `anonymous_required` added; `never_cache` / `require_http_methods` applied where useful.
- **`my_tags.py`**: converted from a `simple_tag` that built raw HTML via f-strings to
  an `inclusion_tag` rendering a real template (`partials/_tab_widget.html`) — restores
  autoescaping and normal HTML tooling. `home.html` now actually uses it.
- **Password reset**: replaced the hand-rolled session-token flow with Django's built-in
  `PasswordResetView` / `PasswordResetConfirmView` + `PasswordResetTokenGenerator`
  (stateless, self-expiring, single-use tokens).

Left untouched, per instruction: the hardcoded credentials/comments in `settings.py`,
and the stale root `UserAuthentication/views.py` stub (harmless — Python's import
system resolves the `views/` package before a same-named sibling module, so it's
never actually imported).

## Setup

```bash
python -m venv venv
source venv/bin/activate          # venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # optional, for /admin/
python manage.py runserver
```

OTP / account-created / password-reset / feedback emails print to the console
(`EMAIL_BACKEND = console`), matching the original project's dev setup.

## Running the tests

```bash
python manage.py test
```

Organized as:
```
UserAuthentication/tests/unit/         backends, forms, decorators (no DB-spanning flow)
UserAuthentication/tests/integration/  login, logout, home, feedback, password reset
UserAuthentication/tests/e2e/          full registration wizard: register → OTP → credentials
```

**A note on how this was produced:** this refactor was written and reviewed line-by-line
against the original codebase, but the sandbox used to generate it has no network
access, so `pip install Django django-formtools` could not be run here, and the test
suite above could not actually be executed end-to-end before packaging. Every view,
form, URL, and template was hand-traced against Django 5.1 / django-formtools'
documented behavior (wizard step-prefixing, `PasswordResetConfirmView`'s token-in-session
redirect, `login()` needing an explicit `backend=` when multiple `AUTHENTICATION_BACKENDS`
are configured, etc.), but please run `python manage.py test` yourself after installing
the requirements — and open an issue/let me know what you find if anything fails.

## Future work

- `validate_employee_id_exists()` in `services/employee_validation.py` is a deliberate
  no-op placeholder for the future external HR-system integration.
- Consider `django-ratelimit` on `login`, `forgot_password`, and the OTP step.
- Consider a JS strength meter (e.g. `zxcvbn`) on the credentials step for live feedback,
  in addition to the server-side `validate_password()` check.
