from django.contrib.auth.models import AbstractUser
from django.db.models.functions import Lower
from django.db import models

class User(AbstractUser):
    class UserRole(models.TextChoices):
        USER = "user", "Користувач"
        SHELTER = "shelter", "Притулок"

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
    )

    @property
    def is_shelter(self):
        return self.role == self.UserRole.SHELTER

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('email'),
                name='unique_user_email_case_insensitive',
            ),
        ]
