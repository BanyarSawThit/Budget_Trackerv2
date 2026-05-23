import calendar
import csv
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date, datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from calendar import month_name

from expenses.forms import ExpenseForm
from expenses.models import Expense, User, Income, SHARED_CATEGORIES, Deposit, CATEGORY_CHOICES

from expenses.notifications import notify_user
from expenses.services import get_user_stats, get_deposit, get_opening_budget, get_shared_expenses, get_saving
from expenses.utils import get_int, get_selected_period, get_selected_user


@login_required
def expense_list(request):
    users = User.objects.all()
    month_range = range(1, 13)
    current_year = date.today().year
    year_range = range(current_year - 2, current_year + 3)

    selected_month, selected_year = get_selected_period(request)

    selected_user = get_int(request.GET.get('user'), 0)
    selected_category = request.GET.get('category', '')

    expenses = (Expense.objects
                .select_related('user')
                .filter(date__month=selected_month,
                        date__year=selected_year))

    if selected_user != 0:
        expenses = expenses.filter(user_id=selected_user)

    if selected_category:
        expenses = expenses.filter(category=selected_category)

    context = {
        'expenses': expenses,
        'users': users,
        'selected_user': selected_user,
        'selected_category': selected_category,
        'category_choices': CATEGORY_CHOICES,

        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_range': month_range,
        'year_range': year_range,
    }

    return render(request, 'expenses/expense_list.html', context)


@login_required
def add_expense(request):

    """Add new expense and show today's summary"""

    current_user = request.user

    session_month = request.session.get("selected_month", date.today().month)
    session_year = request.session.get("selected_year", date.today().year)

    # User total budget before adding expense
    user_stats = get_user_stats(current_user, session_month, session_year)
    deposit = get_deposit(session_month, session_year)

    # today spent total
    today_total = (Expense.objects
                   .filter(date=date.today())
                   .aggregate(Sum("amount"))['amount__sum'] or 0)

    # today expense list
    today_list = Expense.objects.filter(date=date.today())

    # ADD FORM
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = current_user
            expense.save()

            if expense.category in SHARED_CATEGORIES:
                deposit = deposit - expense.amount
                notify_user(
                    added_by_username=request.user.username,
                    amount=expense.amount,
                    category=expense.get_category_display(),
                    description=expense.description,
                    deposit=deposit,
                )
            else:
                budget = user_stats['balance'] - expense.amount
                notify_user(
                    added_by_username=request.user.username,
                    amount=expense.amount,
                    category=expense.get_category_display(),
                    description=expense.description,
                    budget=budget,
                )


            return redirect('add_expense')
    else:
        form = ExpenseForm()

    context = {
        'form': form,
        'today_total': today_total,
        'user_stats': user_stats,
        'today_list': today_list,
        'user': current_user,
    }
    return render(request, 'expenses/add_expense.html', context)


@login_required
def edit_expense(request, id):
    item = get_object_or_404(Expense, id=id, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=item)
    return render(request, 'expenses/edit_expense.html', {'form': form, 'item': item })


@login_required
def delete_expense(request, id):
    item = get_object_or_404(Expense, id=id, user=request.user)
    if request.method == 'POST':
        item.delete()
        return redirect('expense_list')
    return render(request, 'expenses/delete_expense.html', {'item': item})


@login_required
def summary(request):

    month_range = range(1, 13)

    selected_month, selected_year = get_selected_period(request)
    selected_month_name = month_name[selected_month]

    if selected_month == 1:
        prev_month, prev_year = 12, selected_year - 1
    else:
        prev_month, prev_year = selected_month - 1, selected_year

    all_user = list(User.objects.all())
    user_stats_list = []

    month_deposit = (Deposit.objects
                     .filter(date__month=selected_month,date__year=selected_year)
                     .aggregate(Sum('amount'))['amount__sum'] or 0)

    shared_monthly_total = (Expense.objects
                            .filter(category__in=SHARED_CATEGORIES, date__month=selected_month,date__year=selected_year)
                            .aggregate(Sum('amount'))['amount__sum'] or 0)
    remaining_deposit = month_deposit - shared_monthly_total

    for user in all_user:
        user_stats = get_user_stats(user, selected_month, selected_year)
        opening_budget = get_opening_budget(user, selected_month, selected_year)
        available_budget = user_stats['income'] + opening_budget - user_stats['deposit']
        budget_left = available_budget - user_stats['personal_ex']
        pct = int(user_stats['personal_ex'] / available_budget * 100) if available_budget > 0 else 0

        user_stats_list.append({
            'user': user,
            'stats': user_stats,
            'available_budget': available_budget,
            'budget_left': budget_left,
            'pct': pct,
        })

    today = date.today()
    if selected_month == today.month and selected_year == today.year:
        days_in_month = Decimal(today.day)
    else:
        days_in_month = Decimal(calendar.monthrange(selected_year, selected_month)[1])

    combined_balance= 0
    spent_total = 0
    for item in user_stats_list:
        combined_balance += item['stats']['net_balance']
        spent_total += item['stats']['personal_ex']

    daily_avg = spent_total / days_in_month if days_in_month > 0 else 0

    user_stats_list.sort(key=lambda x: x['stats']['net_balance'], reverse=True)

    current_user_stats = next(
        (item for item in user_stats_list if item['user'] == request.user),
        None
    )

    shared_food, shared_grocery, shared_utility = get_shared_expenses(selected_month, selected_year)
    prev_shared_food, prev_shared_grocery, prev_shared_utility = get_shared_expenses(prev_month, prev_year)


    context = {
        'user_stats': user_stats_list,
        'current_user_stats':current_user_stats,

        'month_range': month_range,
        'selected_month': selected_month,
        'selected_month_name': selected_month_name,

        'combined_balance': combined_balance,
        'daily_avg': daily_avg,
        'spent_total': spent_total,

        # Deposit details
        'remaining_deposit': remaining_deposit,
        'shared_food': shared_food,
        'shared_grocery': shared_grocery,
        'shared_utility': shared_utility,
        'prev_shared_food': prev_shared_food,
        'prev_shared_grocery':prev_shared_grocery,
        'prev_shared_utility':prev_shared_utility,
    }
    return render(request, 'expenses/summary.html', context)


@login_required
def export_expense_csv(request):

    expenses = (Expense.objects.
                select_related('user')
                .filter(date__month=datetime.today().month,
                        date__year=datetime.today().year)
                .order_by('date'))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expense.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'User', 'Category', 'Amount', 'Description'])

    for e in expenses:
        writer.writerow([e.date, e.user.username, e.get_category_display(), e.amount, e.description])

    return response


@login_required
def user_detail(request):

    users = User.objects.all()
    month_range = range(1, 13)

    selected_user_id = get_selected_user(request)
    selected_user = get_object_or_404(User, id=selected_user_id)

    selected_month, selected_year = get_selected_period(request)
    selected_month_name = month_name[selected_month]

    user_stats = get_user_stats(selected_user, selected_month, selected_year)
    opening_budget = get_opening_budget(selected_user, selected_month, selected_year)
    available_budget = user_stats['income'] + opening_budget - user_stats['deposit']

    expenses = (Expense.objects
                .filter(user=selected_user, date__month=selected_month, date__year=selected_year)
                .exclude(category__in=SHARED_CATEGORIES).order_by('-amount'))

    incomes = (Income.objects
               .filter(user=selected_user, date__month=selected_month, date__year=selected_year))

    context = {
        'users': users,
        'selected_user': selected_user,
        'selected_month': selected_month,
        'selected_year': selected_year,

        'month_name': selected_month_name,
        'month_range': month_range,

        'user_stats': user_stats,
        'available_budget': available_budget,
        'all_saving_total': get_saving(selected_user),

        'expenses': expenses,
        'incomes': incomes,

    }
    return render(request, 'expenses/user_detail.html', context)