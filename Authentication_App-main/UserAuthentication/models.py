from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class CustomUser(AbstractUser):
    employee_id = models.CharField(max_length=5, unique=True)

    def clean(self):
        # Custom validation for employee ID format
        if not self.employee_id.isdigit():
            raise ValidationError('Employee ID must be a 5-digit number.')
        super().clean()