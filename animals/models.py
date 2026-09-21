from django.db import models
from django.conf import settings

class Animal(models.Model):

    class Species(models.TextChoices):
        DOG = "dog", "Собака"
        CAT = "cat", "Кіт"
        RABBIT = "rabbit", "Кролик"
        RODENT = "rodent", "Гризун"
        BIRD = "bird", "Птах"
        OTHER = "other", "Інша тварина"

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Шукає домівку'
        ADOPTED = 'adopted', 'Усиновлена'
        ARCHIVED = 'archived', 'В архіві'

    name = models.CharField(max_length=150, verbose_name="Ім'я")
    age = models.PositiveIntegerField(
        verbose_name='Вік у місяцях',
        help_text='Вкажіть приблизний вік у повних місяцях. Наприклад, 24 – це 2 роки.',
    )

    species = models.CharField(
        max_length=50,
        choices=Species.choices,
        default=Species.OTHER,
        verbose_name="Вид")

    description = models.TextField(verbose_name="Опис тварини")

    adoption_status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.AVAILABLE,
        verbose_name="Статус"
    )

    main_photo = models.ImageField(
        blank=True,
        upload_to='animals/',
        verbose_name='Фото тварини'
    )

    shelter = models.ForeignKey(
        "shelters.Shelter",
        on_delete=models.PROTECT,
        related_name="animals",
        verbose_name="Притулок"
    )

    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="favorites",
        verbose_name="Додали в обране",
    )

    class Meta:
        verbose_name = 'Тварина'
        verbose_name_plural = 'Тварини'

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        return self.adoption_status == self.Status.AVAILABLE

    @property
    def age_years(self):
        return self.age // 12

    @property
    def age_remaining_months(self):
        return self.age % 12


class AnimalImage(models.Model):
    image = models.ImageField(
        upload_to='animals/gallery/',
        verbose_name='Фото'
    )

    animal = models.ForeignKey(
        "animals.Animal",
        related_name='images',
        on_delete=models.CASCADE,
        verbose_name="Тварина"
    )

    class Meta:
        verbose_name = 'Фото тварини'
        verbose_name_plural = 'Фотографії тварин'

    def __str__(self):
        return f'Фото {self.animal.name} (#{self.pk})'

class AnimalUpdate(models.Model):
    message = models.TextField(verbose_name='Текст новини')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата створення',
    )

    animal = models.ForeignKey(
        'animals.Animal',
        related_name='updates',
        on_delete=models.PROTECT,
        verbose_name='Тварина',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Новина про тварину'
        verbose_name_plural = 'Новини про тварин'

    def __str__(self):
        return f'Новина про {self.animal.name} (#{self.pk})'