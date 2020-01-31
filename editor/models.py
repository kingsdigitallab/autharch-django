from django.contrib.auth.models import User
from django.db import models


class EditorProfile(models.Model):

    ADMIN = 'AD'
    MODERATOR = 'MO'
    EDITOR = 'ED'
    VISITOR = 'VI'
    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator'),
        (EDITOR, 'Editor'),
        (VISITOR, 'Visitor'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='editor_profile')
    role = models.CharField(max_length=2, choices=ROLE_CHOICES,
                            default=VISITOR)
