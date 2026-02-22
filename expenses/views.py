# expenses/views
from unicodedata import category

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404


from .forms import ExpenseForm
from .models import Expense, User, Income, SHARED_CATEGORIES

@login_required
def expense(request):
    expenses = Expense.objects.all()

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
    """
    1. Add expense
    2. choose category
    3. submit
    """

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

    total_budget = Income.objects.all().aggregate(Sum('amount'))['amount__sum'] or 0
    total_spent = Expense.objects.all().aggregate(Sum('amount'))['amount__sum'] or 0
    total_left = total_budget - total_spent

    def get_user_stat(user):
        budget = Income.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        spent = Expense.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        left = budget - spent
        for_both = (Expense.objects
                    .filter(user=user, category__in=SHARED_CATEGORIES)
                    .aggregate(Sum('amount'))
                    )['amount__sum'] or 0
        for_self = (Expense.objects
                    .filter(user=user)
                    .exclude(category__in=SHARED_CATEGORIES)
                    .aggregate(Sum('amount'))
                    )['amount__sum'] or 0

        return {
            'budget' : budget,
            'spent' : spent,
            'left' : left,
            'for_both' : for_both,
            'for_self': for_self
        }

    user1_stats = get_user_stat(current_user)
    user2_stats = get_user_stat(other_user)

    context = {
        'total_budget' : total_budget,
        'total_spent': total_spent,
        'total_left': total_left,
        'user1_stats': user1_stats,
        'user2_stats': user2_stats,
        'user1_name': current_user.username,
        'user2_name': other_user.username,
    }
    return render(request, 'expenses/user_summary.html', context)


def add_income():
    return None