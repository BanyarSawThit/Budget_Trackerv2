from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404

from expenses.forms import IncomeForm
from expenses.models import Income, Deposit, Expense, SHARED_CATEGORIES

from expenses.notifications import notify_user


@login_required
def list_income(request):
    income = Income.objects.select_related('user').all()

    income_data = {}

    for item in income:
        income_data[item.id] = {
            'id': item.id,
            'user': item.user,
            'amount': item.amount,
            'date': item.date,
            'description': item.description
        }

    context = {
        'income_data': income_data,
    }
    return render(request, 'income/income_list.html', context)


@login_required
def add_income(request):

    current_user = request.user
    income_qs = Income.objects.select_related('user').all()
    current_month_income_amount = (income_qs
                         .filter(user=current_user,
                                 date__month=date.today().month,
                                 date__year=date.today().year)
                         .aggregate(Sum('amount'))['amount__sum'] or 0)
    current_month_income_list = income_qs.filter(date__month=date.today().month
                                              ,date__year=date.today().year)

    # GET USER BUDGET
    income_amount = (Income.objects
              .filter(user=current_user, date__month=date.today().month, date__year=date.today().year)
              .aggregate(Sum('amount'))['amount__sum'] or 0)
    deposit = (Deposit.objects
               .filter(user=current_user, date__month=date.today().month, date__year=date.today().year)
               .aggregate(Sum('amount'))['amount__sum'] or 0)
    spent = (Expense.objects
             .filter(user=current_user, date__month=date.today().month, date__year=date.today().year)
             .exclude(category__in=SHARED_CATEGORIES)
             .aggregate(Sum('amount'))['amount__sum'] or 0)

    income_data = {}

    for item in current_month_income_list:
        income_data[item.id] = {
            'id': item.id,
            'user': item.user,
            'amount': item.amount,
            'date': item.date,
            'description': item.description
        }

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            new_income = form.save(commit=False)
            new_income.user = current_user
            new_income.save()

            # User's budget left
            budget = (income_amount + new_income.amount) - deposit - spent

            notify_user(
                added_by_username=request.user.username,
                amount=new_income.amount,
                category="Income",
                description=new_income.description,
                budget=budget,
            )

            return redirect('add_income')
    else:
        form = IncomeForm()

    context = {
        'form': form,
        'current_month': date.today().strftime("%B"),
        'current_month_income_amount': current_month_income_amount,
        'income_data': income_data,

    }
    return render(request, 'income/add_income.html', context)


@login_required
def edit_income(request, id):
    income = get_object_or_404(Income, id=id, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            return redirect('add_income')
    else:
        form = IncomeForm(instance=income)

    return render(request, 'income/edit_income.html', {'form': form, 'item': income})


@login_required
def delete_income(request, id):
    income = get_object_or_404(Income, id=id, user=request.user)
    if request.method == 'POST':
        income.delete()
        return redirect('income_list')
    return render(request, 'income/delete_income.html', {'item': income})
