from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404

from expenses.forms import IncomeForm
from expenses.models import Income

from expenses.notifications import notify_other_user


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
    return render(request, 'expenses/income_list.html', context)


@login_required
def add_income(request):

    income = Income.objects.select_related('user').all()
    current_month_income_amount = (income
                         .filter(date__month=date.today().month,
                                 date__year=date.today().year)
                         .aggregate(Sum('amount'))['amount__sum'] or 0)
    current_month_income_list = income.filter(date__month=date.today().month
                                              ,date__year=date.today().year)

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
            income = form.save(commit=False)
            income.user = request.user
            income.save()

            notify_other_user(
                added_by_username=request.user.username,
                amount=income.amount,
                category="Income",
                description=income.description
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
    return render(request, 'expenses/add_income.html', context)


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

    return render(request, 'expenses/edit_income.html', {'form': form, 'item': income})


@login_required
def delete_income(request, id):
    income = get_object_or_404(Income, id=id, user=request.user)
    if request.method == 'POST':
        income.delete()
        return redirect('income_list')
    return render(request, 'expenses/delete_income.html', {'item': income})
