from decimal import Decimal
from datetime import date
from django.db import models
from django.utils import timezone
import math


class AppSetting(models.Model):
    user_display_name = models.CharField(max_length=50, default='Sahabat Menabung')
    currency_symbol = models.CharField(max_length=10, default='Rp')
    date_format = models.CharField(max_length=20, default='DD/MM/YYYY')
    reminder_enabled = models.BooleanField(default=True)
    reminder_time = models.TimeField(default='20:00:00')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pengaturan ({self.user_display_name})"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


class SavingsGoal(models.Model):
    FREQUENCY_CHOICES = [
        ('DAILY', 'Harian'),
        ('WEEKLY', 'Mingguan'),
        ('MONTHLY', 'Bulanan'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Aktif'),
        ('ACHIEVED', 'Tercapai'),
        ('CANCELLED', 'Dibatalkan'),
    ]

    COLOR_CHOICES = [
        ('blue', 'Sky Cyan (#7FCFFF)'),
        ('emerald', 'Mint Green (#6DD58C)'),
        ('violet', 'Lavender (#D0BCFF)'),
        ('amber', 'Warm Gold (#FFD270)'),
        ('rose', 'Soft Coral (#FFB4AB)'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon_name = models.CharField(max_length=50, default='savings')
    color_theme = models.CharField(max_length=20, choices=COLOR_CHOICES, default='blue')
    IMAGE_RATIO_CHOICES = [
        ('1:1', 'Kotak (1:1)'),
        ('4:3', 'Landscape (4:3)'),
        ('3:4', 'Portrait (3:4)'),
        ('16:9', 'Widescreen (16:9)'),
    ]

    image = models.ImageField(upload_to='goals/', blank=True, null=True)
    image_ratio = models.CharField(max_length=10, choices=IMAGE_RATIO_CHOICES, default='4:3', blank=True)
    target_amount = models.DecimalField(max_digits=14, decimal_places=2)
    current_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=10, default='IDR')
    start_date = models.DateField(default=timezone.now)
    target_date = models.DateField(null=True, blank=True)
    period_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='DAILY')
    planned_amount_per_period = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def progress_percentage(self):
        if not self.target_amount or self.target_amount <= Decimal('0.00'):
            return 0
        pct = (self.current_amount / self.target_amount) * Decimal('100')
        return min(100, max(0, round(float(pct), 1)))

    @property
    def remaining_amount(self):
        rem = self.target_amount - self.current_amount
        return max(Decimal('0.00'), rem)

    @property
    def estimated_periods_remaining(self):
        if self.planned_amount_per_period and self.planned_amount_per_period > 0:
            rem = self.remaining_amount
            if rem <= 0:
                return 0
            return math.ceil(float(rem / self.planned_amount_per_period))
        return None

    @property
    def estimated_days_remaining(self):
        periods = self.estimated_periods_remaining
        if periods is None:
            return None
        if self.period_frequency == 'DAILY':
            return periods
        elif self.period_frequency == 'WEEKLY':
            return periods * 7
        elif self.period_frequency == 'MONTHLY':
            return periods * 30
        return periods

    @property
    def estimated_time_remaining_label(self):
        periods = self.estimated_periods_remaining
        if periods is None:
            return None
        if self.period_frequency == 'DAILY':
            return f"{periods} hari lagi"
        elif self.period_frequency == 'WEEKLY':
            return f"{periods} minggu lagi"
        elif self.period_frequency == 'MONTHLY':
            return f"{periods} bulan lagi"
        return f"{periods} periode lagi"

    @property
    def days_remaining(self):
        if not self.target_date:
            return None
        today = date.today()
        diff = (self.target_date - today).days
        return max(0, diff)

    @property
    def periods_remaining(self):
        days = self.days_remaining
        if days is None:
            return self.estimated_periods_remaining or 1
        if days <= 0:
            return 1
        if self.period_frequency == 'DAILY':
            return days
        elif self.period_frequency == 'WEEKLY':
            return max(1, math.ceil(days / 7))
        elif self.period_frequency == 'MONTHLY':
            return max(1, math.ceil(days / 30))
        return days

    @property
    def recommended_periodic_amount(self):
        if self.planned_amount_per_period and self.planned_amount_per_period > 0:
            return self.planned_amount_per_period
        periods = self.periods_remaining
        if not periods or periods <= 0:
            return self.remaining_amount
        rec = self.remaining_amount / Decimal(str(periods))
        return round(rec, 0)

    def recalculate_current_amount(self):
        deposits = self.transactions.filter(transaction_type='DEPOSIT').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        withdraws = self.transactions.filter(transaction_type='WITHDRAW').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        new_total = deposits - withdraws
        self.current_amount = max(Decimal('0.00'), new_total)

        if self.current_amount >= self.target_amount and self.target_amount > 0:
            self.status = 'ACHIEVED'
        elif self.status == 'ACHIEVED' and self.current_amount < self.target_amount:
            self.status = 'ACTIVE'

        self.save(update_fields=['current_amount', 'status', 'updated_at'])


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Tambah'),
        ('WITHDRAW', 'Kurangi'),
    ]

    goal = models.ForeignKey(SavingsGoal, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='DEPOSIT')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    transaction_date = models.DateField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-transaction_date', '-created_at']

    def __str__(self):
        sign = '+' if self.transaction_type == 'DEPOSIT' else '-'
        return f"{self.goal.name}: {sign}{self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.goal.recalculate_current_amount()

    def delete(self, *args, **kwargs):
        goal = self.goal
        super().delete(*args, **kwargs)
        goal.recalculate_current_amount()


class SavingsReminder(models.Model):
    FREQUENCY_CHOICES = [
        ('DAILY', 'Harian'),
        ('WEEKLY', 'Mingguan'),
        ('MONTHLY', 'Bulanan'),
    ]

    goal = models.ForeignKey(SavingsGoal, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField(max_length=120)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='DAILY')
    reminder_time = models.TimeField(default='20:00:00')
    is_active = models.BooleanField(default=True)
    last_notified_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Pengingat: {self.title} ({self.frequency})"
