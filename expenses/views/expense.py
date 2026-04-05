import csv

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date, datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from calendar import month_name

from expenses.forms import ExpenseForm
from expenses.models import Expense, User, Income, SHARED_CATEGORIES, Deposit, CATEGORY_CHOICES

from expenses.notifications import notify_user
from expenses.services import get_user_stats


@login_required
def expense_list(request):
    month_range = range(1, 13)
    users = User.objects.all()
    current_year = date.today().year
    year_range = range(current_year - 2, current_year + 3)

    def get_int(value, default):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    # Get selected month from session or default to current date and session save
    session_month = request.session.get("selected_month", date.today().month)
    selected_month = get_int(request.GET.get('month'), session_month)
    request.session["selected_month"] = selected_month
    selected_month_name = month_name[selected_month]

    # Get selected year from session or default to current date and session save
    session_year = request.session.get("selected_year", date.today().year)
    selected_year = get_int(request.GET.get('year'), session_year)
    request.session["selected_year"] = selected_year

    selected_user = get_int(request.GET.get('user'), 0)
    selected_category = request.GET.get('category', '')
    selected_search = request.GET.get('search', '')


    expenses = (Expense.objects
                .select_related('user')
                .filter(date__month=selected_month,
                        date__year=selected_year))

    if selected_user != 0:
        expenses = expenses.filter(user_id=selected_user)

    top_cats = {}
    for code, name in CATEGORY_CHOICES:
        top_cats[name] = (expenses
                          .filter(category=code)
                          .aggregate(Sum('amount'))['amount__sum'] or 0)
    top_cats = dict(sorted(top_cats.items(), key=lambda item: item[1], reverse=True))

    if selected_category:
        expenses = expenses.filter(category=selected_category)

    if selected_search:
        expenses = expenses.filter(description__icontains=selected_search)

    month_total = (expenses.aggregate(Sum('amount'))['amount__sum'] or 0)

    shared_total = (expenses
                       .filter(category__in=SHARED_CATEGORIES)
                       .aggregate(Sum('amount'))['amount__sum'] or 0)

    personal_total = (expenses
                         .exclude(category__in=SHARED_CATEGORIES)
                         .aggregate(Sum('amount'))['amount__sum'] or 0)

    context = {
        'expenses': expenses,
        'users': users,
        'selected_user': selected_user,
        'selected_category': selected_category,
        'category_choices': CATEGORY_CHOICES,
        'top_cats': top_cats,
        'selected_search': selected_search,

        'month_total': month_total,
        'shared_total': shared_total,
        'personal_total': personal_total,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'selected_month_name': selected_month_name,
        'month_range': month_range,
        'year_range': year_range,
        'current_month': date.today().month,
        'current_year': date.today().year,
    }

    return render(request, 'expenses/expense_list.html', context)


@login_required
def add_expense(request):

    """Add new expense and show today's summary"""

    current_user = request.user

    # User total budget before adding expense
    user_stats = get_user_stats(current_user, date.today().month, date.today().year)

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
                budget = user_stats['budget_left']
            else:
                budget = user_stats['budget_left'] - expense.amount

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
        'user_budget_left':user_stats['budget_left'],
        'today_list': today_list,
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

    # === MONTH FILTER ===
    month_range = range(1, 13)
    session_month = request.session.get("selected_month", date.today().month)

    def get_int(value, default):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    # Get selected month from session or default to current date and session save
    session_month = request.session.get("selected_month", date.today().month)
    selected_month = get_int(request.GET.get('month'), session_month)
    request.session["selected_month"] = selected_month
    selected_month_name = month_name[selected_month]

    # Get selected year from session or default to current date and session save
    session_year = request.session.get("selected_year", date.today().year)
    selected_year = get_int(request.GET.get('year'), session_year)
    request.session["selected_year"] = selected_year

    all_user = list(User.objects.all())
    user_stats_list = []

    # === OVERALL TOTALS ===
    monthly_income = (Income.objects
                    .filter(date__month=selected_month,date__year=selected_year)
                    .aggregate(Sum('amount'))['amount__sum'] or 0)
    monthly_deposit = (Deposit.objects
                     .filter(date__month=selected_month,date__year=selected_year)
                     .aggregate(Sum('amount'))['amount__sum'] or 0)

    # Budget = Income - Deposit (money set aside for shared expenses)
    monthly_budget = monthly_income - monthly_deposit

    # Remaining deposit = What's left in the shared pool
    shared_monthly_total = (Expense.objects
                            .filter(category__in=SHARED_CATEGORIES, date__month=selected_month,date__year=selected_year)
                            .aggregate(Sum('amount'))['amount__sum'] or 0)
    remaining_deposit = monthly_deposit - shared_monthly_total

    # === PERSONAL SPENDING (non-shared) ===
    total_personal_spent = (Expense.objects
                            .filter(date__month=selected_month,date__year=selected_year)
                            .exclude(category__in=SHARED_CATEGORIES)
                            .aggregate(Sum('amount'))
                            ['amount__sum'] or 0)

    # Total budget left = Budget minus personal spending
    monthly_budget_left = monthly_budget - total_personal_spent

    for user in all_user:
        user_stats = get_user_stats(user, selected_month, selected_year)
        user_stats_list.append({
            'user': user,
            'stats': user_stats,
        })

    current_user_stats = next(
        (item for item in user_stats_list if item['user'] == request.user),
        None
    )

    context = {
        'user_stats': user_stats_list,
        'current_user_stats':current_user_stats,

        'month_range': month_range,
        'selected_month': selected_month,
        'selected_month_name': selected_month_name,

        # Overall totals
        'monthly_income' : monthly_income,
        'monthly_deposit': monthly_deposit,
        'monthly_budget': monthly_budget,
        'monthly_budget_left': monthly_budget_left,

        # Deposit details
        'remaining_deposit': remaining_deposit,
    }
    return render(request, 'expenses/user_summary.html', context)


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
