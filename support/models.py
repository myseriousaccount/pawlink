from django.db import models
from django.conf import settings

from django.core.validators import MinValueValidator
from django.db.models.aggregates import Sum
from django.utils import timezone
from decimal import Decimal


class Need(models.Model):
    class Category(models.TextChoices):
        FOOD = 'food', 'Їжа'
        MEDICINE = 'medicine', 'Ліки'
        TREATMENT = 'treatment', 'Лікування'
        CARE = 'care', 'Догляд'
        OTHER = 'other', 'Інше'

    class Frequency(models.TextChoices):
        ONE_TIME = 'one_time', 'Одноразово'
        MONTHLY = 'monthly', 'Щомісяця'

    class Unit(models.TextChoices):
        MONEY = 'money', 'грн'
        WEIGHT =  'weight', 'кг'
        QUANTITY = 'quantity', 'шт'

    name = models.CharField(
        max_length=255,
        verbose_name='Потреба'
    )
    description = models.TextField(
        verbose_name='Опис потреби',
        blank=True
    )

    category = models.CharField(
        max_length=100,
        choices=Category.choices,
        default=Category.OTHER,
        verbose_name='Категорія потреби'
    )

    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.ONE_TIME,
        verbose_name='Періодичність допомоги',
    )

    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Цільове значення'
    )

    unit = models.CharField(
        max_length=20,
        choices=Unit.choices,
        verbose_name='Одиниця вимірювання',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Статус потреби',
    )

    animal = models.ForeignKey(
        'animals.Animal',
        on_delete=models.PROTECT,
        related_name="needs",
        verbose_name="Тварина"
    )

    class Meta:
        verbose_name = 'Потреба тварини'
        verbose_name_plural = 'Потреби тварин'

    def __str__(self):
        return f'{self.name} — {self.animal.name}'

    @property
    def contributed_amount(self):
        contributions = self.contributions.filter(is_approved=True)

        if self.frequency == self.Frequency.MONTHLY:
            today = timezone.localdate()
            contributions = contributions.filter(
                created_at__year=today.year,
                created_at__month=today.month,
            )

        total = contributions.aggregate(
            total=Sum('amount'))['total']

        return total or Decimal('0.00')

    @property
    def progress(self):
        if self.target_amount > 0:
            percentage = (self.contributed_amount / self.target_amount) * Decimal('100')
            return percentage
        return Decimal('0.00')

    @property
    def remaining_amount(self):
        """Обсяг допомоги, який ще залишилося зібрати."""
        remaining = self.target_amount - self.contributed_amount
        return max(remaining, Decimal('0.00'))

    @property
    def is_fulfilled(self):
        """Чи досягнуто цільового обсягу допомоги."""
        return self.contributed_amount >= self.target_amount

    @property
    def can_accept_contributions(self):
        """Чи можна зараз приймати нові внески."""
        return self.is_active and not self.is_fulfilled



class SupportContribution(models.Model):
    supporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='contributions',
        verbose_name='Благодійник',
    )
    need = models.ForeignKey(
        Need,
        on_delete=models.PROTECT,
        related_name='contributions',
        verbose_name='Потреба',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Обсяг допомоги',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата створення',
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name='Внесок підтверджено',
    )

    proof = models.ImageField(
        upload_to='contributions/proofs/',
        blank=True,
        verbose_name='Фото підтвердження допомоги',
    )

    class Meta:
        verbose_name = 'Благодійний внесок'
        verbose_name_plural = 'Благодійні внески'

    def __str__(self):
        return f'Внесок #{self.pk} — {self.need}'