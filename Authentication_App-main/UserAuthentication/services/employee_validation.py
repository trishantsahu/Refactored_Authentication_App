"""
Employee ID validation.

Kept separate from forms.py so the same checks can be reused outside the
registration form (e.g. from a future management command, an admin action,
or an API endpoint) without duplicating logic.

``validate_employee_id_exists`` is a deliberate placeholder: it is the seam
where the future external HR-system lookup will be wired in. Calling it from
RegisterStepForm.clean_employee_id() means that once the real implementation
lands here, the registration wizard automatically rejects unknown employee
IDs *before* an OTP is generated/emailed -- no view or wizard code needs to
change.
"""

from django.core.exceptions import ValidationError

EMPLOYEE_ID_LENGTH = 5


def validate_employee_id_format(employee_id: str) -> None:
    """Employee ID must be exactly EMPLOYEE_ID_LENGTH digits."""
    if not employee_id or not employee_id.isdigit():
        raise ValidationError(
            f"Employee ID must be a {EMPLOYEE_ID_LENGTH}-digit number."
        )
    if len(employee_id) != EMPLOYEE_ID_LENGTH:
        raise ValidationError(
            f"Employee ID must be exactly {EMPLOYEE_ID_LENGTH} digits long."
        )


def validate_employee_id_exists(employee_id: str) -> None:
    """
    Placeholder for the future external HR-system lookup.

    TODO: replace this body with a real call to the external system, e.g.:

        response = external_hr_client.lookup(employee_id)
        if not response.ok:
            raise ValidationError("Employee ID not found in HR records.")

    Until that integration exists, this intentionally does nothing so the
    registration pipeline keeps working unchanged.
    """
    return None
