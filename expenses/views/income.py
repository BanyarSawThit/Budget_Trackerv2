from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404

from expenses.forms import IncomeForm
from expenses.models import Income, User

from expenses.notifications import notify_user
from expenses.services import get_user_stats
from expenses.utils import get_int, get_selected_period


@login_required
def list_income(request):

    users = User.objects.all()
    month_range = range(1,13)

    selected_user = get_int(request.GET.get('user'), request.user.id)

    selected_month, selected_year = get_selected_period(request)

    income = Income.objects.filter(user=selected_user, date__month=selected_month, date__year=selected_year)
    context = {
        'users': users,
        'selected_user': selected_user,
        'month_range': month_range,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'incomes': income,
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
    current_month_income_list = income_qs.filter(user=current_user, date__month=date.today().month
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
            new_income = form.save(commit=False)
            new_income.user = current_user
            new_income.save()

            # Add to User's budget
            user_stats = get_user_stats(current_user, date.today().month, date.today().year)

            notify_user(
                added_by_username=request.user.username,
                amount=new_income.amount,
                category="Income",
                description=new_income.description,
                budget=user_stats['balance'],
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
