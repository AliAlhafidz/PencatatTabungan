from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from savings.models import SavingsGoal, Transaction, SavingsReminder, AppSetting

class Command(BaseCommand):
    help = 'Seeds initial sample data for Celengan'

    def handle(self, *args, **options):
        # Default Settings
        AppSetting.get_solo()

        today = date.today()

        # Goal 1: Beli Laptop
        g1, _ = SavingsGoal.objects.get_or_create(
            name='Beli Laptop Kerja & Kuliah',
            defaults={
                'description': 'Target laptop baru untuk menunjang tugas kuliah dan proyek.',
                'icon_name': 'laptop_mac',
                'color_theme': 'blue',
                'target_amount': Decimal('8500000'),
                'start_date': today - timedelta(days=40),
                'target_date': today + timedelta(days=80),
                'period_frequency': 'WEEKLY',
                'planned_amount_per_period': Decimal('500000'),
                'status': 'ACTIVE',
            }
        )
        if not g1.transactions.exists():
            Transaction.objects.create(goal=g1, transaction_type='DEPOSIT', amount=Decimal('1500000'), transaction_date=today - timedelta(days=35), note='Tabungan awal')
            Transaction.objects.create(goal=g1, transaction_type='DEPOSIT', amount=Decimal('500000'), transaction_date=today - timedelta(days=28), note='Sisa uang saku')
            Transaction.objects.create(goal=g1, transaction_type='DEPOSIT', amount=Decimal('1000000'), transaction_date=today - timedelta(days=14), note='Honor freelance')
            Transaction.objects.create(goal=g1, transaction_type='WITHDRAW', amount=Decimal('200000'), transaction_date=today - timedelta(days=7), note='Keperluan mendesak')
            g1.recalculate_current_amount()

        # Goal 2: Dana Darurat
        g2, _ = SavingsGoal.objects.get_or_create(
            name='Dana Darurat 3 Bulan',
            defaults={
                'description': 'Cadangan dana aman tak terduga.',
                'icon_name': 'shield',
                'color_theme': 'emerald',
                'target_amount': Decimal('5000000'),
                'start_date': today - timedelta(days=60),
                'target_date': today + timedelta(days=120),
                'period_frequency': 'MONTHLY',
                'planned_amount_per_period': Decimal('1000000'),
                'status': 'ACTIVE',
            }
        )
        if not g2.transactions.exists():
            Transaction.objects.create(goal=g2, transaction_type='DEPOSIT', amount=Decimal('1000000'), transaction_date=today - timedelta(days=50), note='Setoran bulan 1')
            Transaction.objects.create(goal=g2, transaction_type='DEPOSIT', amount=Decimal('1200000'), transaction_date=today - timedelta(days=20), note='Setoran bulan 2 + bonus')
            g2.recalculate_current_amount()

        # Goal 3: Sepatu Olahraga (Tercapai)
        g3, _ = SavingsGoal.objects.get_or_create(
            name='Sepatu Olahraga Baru',
            defaults={
                'description': 'Target beli sepatu lari nyaman.',
                'icon_name': 'sports_esports',
                'color_theme': 'amber',
                'target_amount': Decimal('750000'),
                'start_date': today - timedelta(days=30),
                'target_date': today - timedelta(days=2),
                'period_frequency': 'WEEKLY',
                'planned_amount_per_period': Decimal('200000'),
                'status': 'ACTIVE',
            }
        )
        if not g3.transactions.exists():
            Transaction.objects.create(goal=g3, transaction_type='DEPOSIT', amount=Decimal('350000'), transaction_date=today - timedelta(days=25), note='Nabung minggu 1')
            Transaction.objects.create(goal=g3, transaction_type='DEPOSIT', amount=Decimal('400000'), transaction_date=today - timedelta(days=10), note='Nabung minggu 2 (Lunas!)')
            g3.recalculate_current_amount()

        # Reminder
        SavingsReminder.objects.get_or_create(
            goal=g1,
            title='Isi celengan Laptop tiap akhir pekan',
            defaults={
                'frequency': 'WEEKLY',
                'reminder_time': '20:00:00',
                'is_active': True,
            }
        )

        self.stdout.write(self.style.SUCCESS('Sampel data Celengan berhasil di-seed!'))
