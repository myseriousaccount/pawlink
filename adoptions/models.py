from django.db import models
from django.conf import settings

class AdoptionApplication(models.Model):
    class ApplicationStatus(models.TextChoices):
        PENDING = "pending", "На розгляді"
        APPROVED = "approved", "Схвалена"
        REJECTED = "rejected", "Відхилена"

    message = models.TextField(
        verbose_name="Мотиваційний текст"
    )
    status = models.CharField(
        max_length=15,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
        verbose_name="Статус заявки"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата створення заявки"
    )
    updated_at = models.DateTimeField(auto_now=True)
    shelter_comment = models.TextField(
        blank=True,
        verbose_name="Коментар від притулку"
    )

    animal = models.ForeignKey(
        "animals.Animal",
        on_delete=models.PROTECT,
        related_name="adoption_applications",
        verbose_name="Тварина",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="adoption_applications",
        verbose_name="Користувач",
    )

    class Meta:
        verbose_name = 'Заявка на адопцію'
        verbose_name_plural = 'Заявки на адопцію'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'animal'],
                name='unique_user_animal_application',
                violation_error_message='Ви вже подали заявку на цю тварину.',
            ),
        ]

    def __str__(self):
        return f"Заявка на адопцію {self.animal.name} від {self.user.username}"

    @property
    def is_pending(self):
        return self.status == self.ApplicationStatus.PENDING
