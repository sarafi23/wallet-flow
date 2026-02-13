from django.core.exceptions import ValidationError
import re

class ComplexPasswordValidator:
    """
    Validates that a password contains at least:
    - One uppercase letter
    - One number
    """
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                "La contraseña debe contener al menos una letra mayúscula.",
                code='password_no_upper',
            )
        if not re.search(r'\d', password):
            raise ValidationError(
                "La contraseña debe contener al menos un número.",
                code='password_no_number',
            )

    def get_help_text(self):
        return "Tu contraseña debe contener al menos una letra mayúscula y un número."
