from django.core.validators import RegexValidator
from django.db import models


iso_date_validator = RegexValidator(
    regex=r'^-?\d{4}(-\d{2}(-\d{2})?)?$',
    message=('Enter a valid ISO date: YYYY, YYYY-MM, or YYYY-MM-DD '
             '(with optional initial -)')
)


class PartialDateField(models.CharField):

    description = (
        'An ISO 8601 date field that allows for YYYY, YYYY-MM, and '
        'YYYY-MM-DD calendar dates (with optional initial "-").')

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 11  # -YYYY-MM-DD
        super().__init__(*args, **kwargs)
        self.validators.append(iso_date_validator)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs
