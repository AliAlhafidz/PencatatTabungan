from django import forms
from django.utils import timezone
from .models import SavingsGoal, Transaction, AppSetting, SavingsReminder

class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = [
            'name',
            'image',
            'image_ratio',
            'target_amount',
            'period_frequency',
            'planned_amount_per_period',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3.5 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext placeholder-outline focus:outline-none focus:border-primary text-base font-semibold transition-colors',
                'placeholder': 'Contoh: Beli Laptop Baru, Liburan...',
                'required': True,
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'id_image',
                'accept': 'image/*',
            }),
            'target_amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3.5 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext placeholder-outline focus:outline-none focus:border-primary text-xl font-bold transition-colors',
                'placeholder': 'Contoh: 5000000',
                'min': '1000',
                'step': '1000',
                'required': True,
                'id': 'id_target_amount',
            }),
            'period_frequency': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext focus:outline-none focus:border-primary text-sm font-semibold transition-colors',
                'id': 'id_period_frequency',
            }),
            'planned_amount_per_period': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext placeholder-outline focus:outline-none focus:border-primary text-base font-semibold transition-colors',
                'placeholder': 'Nominal per pengisian (Rp)',
                'min': '0',
                'step': '1000',
                'id': 'id_planned_amount_per_period',
            }),
        }



class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'transaction_date', 'note']
        widgets = {
            'transaction_type': forms.HiddenInput(attrs={
                'id': 'id_transaction_type'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3.5 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext placeholder-outline focus:outline-none focus:border-primary text-xl font-bold transition-colors',
                'placeholder': 'Contoh: 50000',
                'min': '1000',
                'step': '1000',
                'required': True,
                'autofocus': True,
            }),
            'transaction_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext placeholder-outline focus:outline-none focus:border-primary text-sm transition-colors',
                'type': 'date',
                'required': True,
            }),
            'note': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext placeholder-outline focus:outline-none focus:border-primary text-sm transition-colors',
                'placeholder': 'Contoh: Sisa uang jajan, Bonus proyek, Hadiah...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('transaction_date'):
            self.initial['transaction_date'] = timezone.now().date().isoformat()


class AppSettingForm(forms.ModelForm):
    class Meta:
        model = AppSetting
        fields = ['user_display_name', 'currency_symbol', 'date_format', 'reminder_enabled', 'reminder_time']
        widgets = {
            'user_display_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext placeholder-outline focus:outline-none focus:border-primary text-base transition-colors',
                'placeholder': 'Nama Anda...',
                'required': True,
            }),
            'currency_symbol': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext placeholder-outline focus:outline-none focus:border-primary text-base transition-colors',
                'placeholder': 'Rp',
                'required': True,
            }),
            'date_format': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext focus:outline-none focus:border-primary text-base transition-colors',
            }, choices=[
                ('DD/MM/YYYY', 'DD/MM/YYYY (Contoh: 19/09/2026)'),
                ('YYYY-MM-DD', 'YYYY-MM-DD (Contoh: 2026-09-19)'),
                ('DD MMM YYYY', 'DD MMM YYYY (Contoh: 19 Sep 2026)'),
            ]),
            'reminder_enabled': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded-lg text-primary focus:ring-primary/40 bg-surface-container-high border-outline/40 accent-primary cursor-pointer',
            }),
            'reminder_time': forms.TimeInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext focus:outline-none focus:border-primary text-base transition-colors',
                'type': 'time',
            }),
        }


class SavingsReminderForm(forms.ModelForm):
    class Meta:
        model = SavingsReminder
        fields = ['goal', 'title', 'frequency', 'reminder_time', 'is_active']
        widgets = {
            'goal': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext focus:outline-none focus:border-primary text-base transition-colors',
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext placeholder-outline focus:outline-none focus:border-primary text-base transition-colors',
                'placeholder': 'Contoh: Waktunya nabung harian!',
                'required': True,
            }),
            'frequency': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext focus:outline-none focus:border-primary text-base transition-colors',
            }),
            'reminder_time': forms.TimeInput(attrs={
                'class': 'w-full px-4 py-3 rounded-2xl bg-surface-container-high border border-outline/30 text-apptext focus:outline-none focus:border-primary text-base transition-colors',
                'type': 'time',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded-lg text-primary focus:ring-primary/40 bg-surface-container-high border-outline/40 accent-primary cursor-pointer',
            }),
        }
