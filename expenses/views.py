# expenses/views
from unicodedata import category

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ExpenseForm
from .models import Expense, User, Income, SHARED_CATEGORIES, Deposit

@login_required
def expense(request):
    expenses = Expense.objects.select_related('user').all()

    items = {}

    for item in expenses:
        items[item.id] = {
            'id': item.id,
            'user': item.user,
            'category': item.get_category_display(),
            'amount': item.amount,
            'date': item.date,
            'created_at': item.created_at,
            'description': item.description
        }

    context = {
        'expense': items
    }

    return render(request, 'expenses/expense.html', context)


@login_required
def add_expense(request):
    """Add new expense and show today's summary"""

    today_total = (Expense.objects
                   .filter(date=date.today())
                   .aggregate(Sum("amount")))['amount__sum'] or 0

    monthly_total = (Expense.objects
                     .filter(date__month=date.today().month, date__year=date.today().year,)
                     .aggregate(Sum("amount")))['amount__sum'] or 0

    today_list = Expense.objects.filter(date=date.today())

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('records')
    else:
        form = ExpenseForm()

    context = {
        'form': form,
        'today_total': today_total,
        'monthly_total': monthly_total,
        'today_list': today_list,
    }
    return render(request, 'expenses/add_expense.html', context)


@login_required
def update_expense(request, id):
    item = get_object_or_404(Expense, id=id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('records')
    else:
        form = ExpenseForm(instance=item)
    return render(request, 'expenses/edit_expense.html', {'form': form})


@login_required
def delete_expense(request, id):
    item = get_object_or_404(Expense, id=id)
    if request.method == 'POST':
        item.delete()
        return redirect('records')
    return render(request, 'expenses/delete_expense.html', {'item': item})


def summary(request):
    current_user = request.user
    other_user = User.objects.exclude(id=current_user.id).first()

    # === OVERALL TOTALS ===
    total_income = Income.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_deposit = Deposit.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_spent = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0

    # Budget = Income - Deposit (money set aside for shared expenses)
    total_budget = total_income - total_deposit

    # === SHARED EXPENSES BREAKDOWN ===
    shared_expenses = Expense.objects.filter(category__in=SHARED_CATEGORIES)

    shared_food = shared_expenses.filter(category='food').aggregate(Sum('amount'))['amount__sum'] or 0
    shared_grocery = shared_expenses.filter(category='grocery').aggregate(Sum('amount'))['amount__sum'] or 0
    shared_utility = shared_expenses.filter(category='utility').aggregate(Sum('amount'))['amount__sum'] or 0

    # Remaining deposit = What's left in the shared pool
    shared_total = shared_food + shared_grocery + shared_utility
    remaining_deposit = total_deposit - shared_total

    # === PERSONAL SPENDING (non-shared) ===
    total_personal_spent = (Expense.objects
                            .exclude(category__in=SHARED_CATEGORIES)
                            .aggregate(Sum('amount'))
                            ['amount__sum'] or 0)

    # Total budget left = Budget minus personal spending
    total_budget_left = total_budget - total_personal_spent

    # === USER STATISTICS ===
    def get_user_stat(user):
        income = Income.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        deposit = Deposit.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0

        # User's budget = their income minus their deposit
        budget = income - deposit

        # User's expenses
        user_expenses = Expense.objects.filter(user=user)
        total_spent = user_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

        for_both = (user_expenses
                      .filter(category__in=SHARED_CATEGORIES)
                      .aggregate(Sum('amount'))['amount__sum'] or 0
                      )
        for_self = (user_expenses
                    .exclude(category__in=SHARED_CATEGORIES)
                    .aggregate(Sum('amount'))['amount__sum'] or 0
                    )


        left = budget - for_self

        return {
            'income' : income,
            'deposit' : deposit,
            'budget' : budget,
            'total_spent' : total_spent,
            'left' : left,
            'for_both' : for_both,
            'for_self': for_self
        }

    user1_stats = get_user_stat(current_user)
    user2_stats = get_user_stat(other_user)

    context = {
        # Overall totals
        'total_income' : total_income,
        'total_deposit': total_deposit,
        'total_budget': total_budget,
        'total_spent': total_spent,
        'total_budget_left': total_budget_left,

        # Deposit details
        'remaining_deposit': remaining_deposit,
        'shared_food': shared_food,
        'shared_grocery': shared_grocery,
        'shared_utility': shared_utility,
        'shared_total': shared_total,

        # User stats
        'user1_stats': user1_stats,
        'user2_stats': user2_stats,
        'user1_name': current_user.username,
        'user2_name': other_user.username,
    }
    return render(request, 'expenses/user_summary.html', context)


def add_income():
    return None