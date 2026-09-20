from datetime import date, timedelta
from decimal import Decimal
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.utils import timezone

from .models import SavingsGoal, Transaction, SavingsReminder, AppSetting
from .forms import SavingsGoalForm, TransactionForm, AppSettingForm, SavingsReminderForm


def get_dashboard_metrics():
    goals = SavingsGoal.objects.all()
    total_goals = goals.count()
    active_goals = goals.filter(status='ACTIVE')
    achieved_goals = goals.filter(status='ACHIEVED')
    
    total_saved = sum(g.current_amount for g in goals)
    total_target = sum(g.target_amount for g in goals)
    
    overall_progress = 0
    if total_target > 0:
        overall_progress = min(100, round(float((total_saved / total_target) * 100), 1))
        
    return {
        'total_saved': total_saved,
        'total_target': total_target,
        'active_count': active_goals.count(),
        'achieved_count': achieved_goals.count(),
        'total_goals_count': total_goals,
        'overall_progress': overall_progress,
    }


def dashboard_view(request):
    status_filter = request.GET.get('status', 'all')
    
    goals_query = SavingsGoal.objects.all()
    if status_filter == 'active':
        goals_query = goals_query.filter(status='ACTIVE')
    elif status_filter == 'achieved':
        goals_query = goals_query.filter(status='ACHIEVED')

    metrics = get_dashboard_metrics()
    reminders = SavingsReminder.objects.filter(is_active=True).select_related('goal')[:3]
    recent_transactions = Transaction.objects.select_related('goal').order_by('-transaction_date', '-created_at')[:5]

    context = {
        'goals': goals_query,
        'metrics': metrics,
        'status_filter': status_filter,
        'reminders': reminders,
        'recent_transactions': recent_transactions,
        'active_tab': 'dashboard',
    }

    if request.htmx and request.htmx.target == 'goal-list-container':
        return render(request, 'savings/partials/goal_list.html', context)

    return render(request, 'savings/dashboard.html', context)


def goals_view(request):
    status_filter = request.GET.get('status', 'all')
    
    goals_query = SavingsGoal.objects.all()
    if status_filter == 'active':
        goals_query = goals_query.filter(status='ACTIVE')
    elif status_filter == 'achieved':
        goals_query = goals_query.filter(status='ACHIEVED')

    context = {
        'goals': goals_query,
        'status_filter': status_filter,
        'active_tab': 'goals',
    }

    if request.htmx and request.htmx.target == 'goal-list-container':
        return render(request, 'savings/partials/goal_list.html', context)

    return render(request, 'savings/goals.html', context)


def goal_create_view(request):
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, request.FILES)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.icon_name = 'savings'
            goal.color_theme = 'blue'
            goal.save()
            
            if request.htmx:
                response = HttpResponse(status=204)
                response['HX-Redirect'] = f"/goals/{goal.pk}/"
                return response
            return redirect('goal_detail', pk=goal.pk)
    else:
        form = SavingsGoalForm(initial={
            'period_frequency': 'WEEKLY',
        })

    return render(request, 'savings/partials/goal_form_modal.html', {
        'form': form,
        'is_edit': False,
    })


def goal_detail_view(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk)
    transactions = goal.transactions.all()
    reminders = goal.reminders.all()

    context = {
        'goal': goal,
        'transactions': transactions,
        'reminders': reminders,
        'active_tab': 'goals',
    }

    if request.htmx and request.htmx.target == 'transactions-list':
        return render(request, 'savings/partials/transaction_list.html', context)

    return render(request, 'savings/goal_detail.html', context)


def goal_edit_view(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk)
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, request.FILES, instance=goal)
        if form.is_valid():
            goal = form.save()
            goal.recalculate_current_amount()
            if request.htmx:
                response = HttpResponse(status=204)
                response['HX-Redirect'] = f"/goals/{goal.pk}/"
                return response
            return redirect('goal_detail', pk=goal.pk)
    else:
        form = SavingsGoalForm(instance=goal)

    return render(request, 'savings/partials/goal_form_modal.html', {
        'form': form,
        'goal': goal,
        'is_edit': True,
    })


def goal_delete_view(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk)
    
    if request.method == 'GET':
        return render(request, 'savings/partials/goal_delete_modal.html', {
            'goal': goal,
        })
        
    goal_name = goal.name
    goal.delete()
    
    if request.htmx:
        response = HttpResponse(status=204)
        response['HX-Redirect'] = '/'
        return response
    return redirect('dashboard')


def transaction_create_view(request, goal_id):
    goal = get_object_or_404(SavingsGoal, pk=goal_id)
    tx_type = request.GET.get('type', 'DEPOSIT')
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.goal = goal
            transaction.save()
            
            if request.htmx:
                # Return refreshed goal detail card & transaction list
                goal.refresh_from_db()
                return render(request, 'savings/partials/goal_progress_card.html', {
                    'goal': goal,
                    'just_achieved': goal.status == 'ACHIEVED',
                })
            return redirect('goal_detail', pk=goal.pk)
    else:
        form = TransactionForm(initial={
            'transaction_type': tx_type,
            'transaction_date': date.today().isoformat()
        })

    return render(request, 'savings/partials/transaction_form_modal.html', {
        'form': form,
        'goal': goal,
        'tx_type': tx_type,
    })


@require_POST
def transaction_delete_view(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    goal = tx.goal
    tx.delete()
    goal.refresh_from_db()
    
    if request.htmx:
        return render(request, 'savings/partials/goal_progress_card.html', {
            'goal': goal,
        })
    return redirect('goal_detail', pk=goal.pk)


def calculator_view(request):
    """
    Kalkulator Rencana Tabungan Interaktif
    """
    return render(request, 'savings/calculator.html', {
        'active_tab': 'calculator'
    })


def calculate_plan_htmx(request):
    try:
        target_amount = Decimal(request.GET.get('target_amount', '0') or '0')
        initial_amount = Decimal(request.GET.get('initial_amount', '0') or '0')
        target_date_str = request.GET.get('target_date', '')
        frequency = request.GET.get('frequency', 'DAILY')

        if not target_date_str or target_amount <= 0:
            return render(request, 'savings/partials/calc_result.html', {'error': 'Silakan masukkan nominal target dan tanggal yang valid.'})

        target_date = date.fromisoformat(target_date_str)
        today = date.today()
        days = (target_date - today).days

        if days <= 0:
            return render(request, 'savings/partials/calc_result.html', {'error': 'Tanggal target harus lebih besar dari hari ini.'})

        remaining_needed = max(Decimal('0'), target_amount - initial_amount)

        if frequency == 'DAILY':
            periods = days
            unit_label = 'Hari'
            period_name = 'Hari'
        elif frequency == 'WEEKLY':
            periods = max(1, (days + 6) // 7)
            unit_label = 'Minggu'
            period_name = 'Minggu'
        else: # MONTHLY
            periods = max(1, (days + 29) // 30)
            unit_label = 'Bulan'
            period_name = 'Bulan'

        nominal_per_period = round(remaining_needed / Decimal(str(periods)), 0)

        context = {
            'target_amount': target_amount,
            'initial_amount': initial_amount,
            'remaining_needed': remaining_needed,
            'days': days,
            'periods': periods,
            'unit_label': unit_label,
            'period_name': period_name,
            'nominal_per_period': nominal_per_period,
            'frequency': frequency,
        }
        return render(request, 'savings/partials/calc_result.html', context)
    except Exception as e:
        return render(request, 'savings/partials/calc_result.html', {'error': f'Terjadi kesalahan: {str(e)}'})


def reminders_view(request):
    reminders = SavingsReminder.objects.select_related('goal').all()
    goals = SavingsGoal.objects.filter(status='ACTIVE')
    form = SavingsReminderForm()

    if request.method == 'POST':
        form = SavingsReminderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reminders')

    return render(request, 'savings/reminders.html', {
        'reminders': reminders,
        'goals': goals,
        'form': form,
        'active_tab': 'reminders',
    })


@require_POST
def reminder_toggle_view(request, pk):
    reminder = get_object_or_404(SavingsReminder, pk=pk)
    reminder.is_active = not reminder.is_active
    reminder.save()
    if request.htmx:
        return render(request, 'savings/partials/reminder_row.html', {'reminder': reminder})
    return redirect('reminders')


@require_POST
def reminder_delete_view(request, pk):
    reminder = get_object_or_404(SavingsReminder, pk=pk)
    reminder.delete()
    if request.htmx:
        return HttpResponse('')
    return redirect('reminders')


def settings_view(request):
    settings = AppSetting.get_solo()
    if request.method == 'POST':
        form = AppSettingForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pengaturan berhasil disimpan!')
            return redirect('settings')
    else:
        form = AppSettingForm(instance=settings)

    return render(request, 'savings/settings.html', {
        'form': form,
        'settings': settings,
        'active_tab': 'settings',
    })


@require_POST
def seed_dummy_data_view(request):
    # Buat sampel target realistis
    today = date.today()

    # Goal 1: Beli Laptop Baru
    g1, _ = SavingsGoal.objects.get_or_create(
        name='Beli Laptop Kerja / Kuliah',
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

    # Goal 3: Sepatu Idaman (Tercapai)
    g3, _ = SavingsGoal.objects.get_or_create(
        name='Sepatu Olahraga Baru',
        defaults={
            'description': 'Target beli sepatu lari nyaman.',
            'icon_name': 'sprint',
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

    messages.success(request, 'Sampel data tabungan berhasil dibuat!')
    return redirect('dashboard')


@require_POST
def reset_all_data_view(request):
    Transaction.objects.all().delete()
    SavingsReminder.objects.all().delete()
    SavingsGoal.objects.all().delete()
    messages.info(request, 'Semua data target dan transaksi telah direset.')
    return redirect('dashboard')


def manifest_view(request):
    from django.conf import settings
    manifest_path = settings.BASE_DIR / 'static' / 'manifest.json'
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='application/manifest+json')


def service_worker_view(request):
    from django.conf import settings
    sw_path = settings.BASE_DIR / 'static' / 'sw.js'
    with open(sw_path, 'r', encoding='utf-8') as f:
        content = f.read()
    response = HttpResponse(content, content_type='application/javascript; charset=utf-8')
    response['Service-Worker-Allowed'] = '/'
    return response

