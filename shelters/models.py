from django.db import models
from django.conf import settings

class Shelter(models.Model):
    class ShelterStatus(models.TextChoices):
        PENDING = 'pending', 'Очікує перевірки'
        APPROVED = 'approved', 'Перевірений'
        REJECTED = 'rejected', 'Перевірку не пройшов'
        INACTIVE = 'inactive', 'Неактивний'

    name = models.CharField(max_length=200, verbose_name='Назва притулку')
    description = models.TextField(verbose_name='Опис притулку')
    city = models.CharField(max_length=200, verbose_name='Місто')
    address = models.CharField(max_length=200, verbose_name='Адреса')
    phone = models.CharField(max_length=30, verbose_name='Номер телефону')
    email = models.EmailField(max_length=200, verbose_name='Електронна пошта')
    website = models.URLField(max_length=200, blank=True, verbose_name='Вебсайт')

    status = models.CharField(
        max_length=20,
        choices=ShelterStatus.choices,
        default=ShelterStatus.PENDING,
        verbose_name='Статус притулку'
    )
    logo = models.ImageField(
        blank=True,
        upload_to='shelters/',
        verbose_name='Логотип притулку',
    )

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shelter",
        verbose_name="Власник притулку",
    )

    class Meta:
        verbose_name = 'Притулок'
        verbose_name_plural = 'Притулки'

    def __str__(self):
        return self.name

    @property
    def is_verified(self):
        return self.status == self.ShelterStatus.APPROVED