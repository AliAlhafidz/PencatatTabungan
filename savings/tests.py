from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from .models import SavingsGoal, Transaction, SavingsReminder, AppSetting


class SavingsGoalModelTests(TestCase):
    def setUp(self):
        self.today = date.today()
        self.goal = SavingsGoal.objects.create(
            name='Test Laptop',
            target_amount=Decimal('10000000'),
            start_date=self.today,
            target_date=self.today + timedelta(days=100),
            period_frequency='WEEKLY',
            status='ACTIVE'
        )

    def test_initial_values(self):
        self.assertEqual(self.goal.current_amount, Decimal('0.00'))
        self.assertEqual(self.goal.progress_percentage, 0)
        self.assertEqual(self.goal.remaining_amount, Decimal('10000000'))
        self.assertEqual(self.goal.status, 'ACTIVE')

    def test_deposit_transaction_updates_goal(self):
        Transaction.objects.create(
            goal=self.goal,
            transaction_type='DEPOSIT',
            amount=Decimal('2500000'),
            transaction_date=self.today,
            note='Gaji pertama'
        )
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.current_amount, Decimal('2500000'))
        self.assertEqual(self.goal.progress_percentage, 25.0)
        self.assertEqual(self.goal.remaining_amount, Decimal('7500000'))

    def test_withdraw_transaction_reduces_balance(self):
        Transaction.objects.create(
            goal=self.goal,
            transaction_type='DEPOSIT',
            amount=Decimal('5000000'),
            transaction_date=self.today
        )
        Transaction.objects.create(
            goal=self.goal,
            transaction_type='WITHDRAW',
            amount=Decimal('1000000'),
            transaction_date=self.today
        )
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.current_amount, Decimal('4000000'))
        self.assertEqual(self.goal.progress_percentage, 40.0)

    def test_goal_achieved_status_transition(self):
        Transaction.objects.create(
            goal=self.goal,
            transaction_type='DEPOSIT',
            amount=Decimal('10000000'),
            transaction_date=self.today
        )
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.status, 'ACHIEVED')
        self.assertEqual(self.goal.progress_percentage, 100.0)


class SavingsViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.today = date.today()
        self.goal = SavingsGoal.objects.create(
            name='Dana Darurat',
            target_amount=Decimal('5000000'),
            start_date=self.today,
            target_date=self.today + timedelta(days=60),
            period_frequency='MONTHLY'
        )

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Celengan')
        self.assertContains(response, 'Dana Darurat')

    def test_goal_detail_view(self):
        response = self.client.get(reverse('goal_detail', args=[self.goal.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dana Darurat')

    def test_calculator_api(self):
        target_date = (self.today + timedelta(days=30)).isoformat()
        response = self.client.get(reverse('calculate_plan'), {
            'target_amount': '3000000',
            'initial_amount': '0',
            'target_date': target_date,
            'frequency': 'DAILY'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rekomendasi Setoran')

    def test_seed_dummy_data(self):
        response = self.client.post(reverse('seed_dummy_data'))
        self.assertEqual(response.status_code, 302)
        # Should have populated sample goals
        self.assertTrue(SavingsGoal.objects.filter(name__icontains='Laptop').exists())

    def test_goal_create_with_image(self):
        import io
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile

        image_io = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='blue')
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        uploaded_image = SimpleUploadedFile('test_goal.jpg', image_io.read(), content_type='image/jpeg')

        response = self.client.post(reverse('goal_create'), {
            'name': 'Goal Dengan Foto',
            'target_amount': '2500000',
            'period_frequency': 'MONTHLY',
            'planned_amount_per_period': '500000',
            'image': uploaded_image
        })
        self.assertEqual(response.status_code, 302)
        goal = SavingsGoal.objects.get(name='Goal Dengan Foto')
        self.assertTrue(bool(goal.image))
        self.assertEqual(goal.target_amount, Decimal('2500000'))

