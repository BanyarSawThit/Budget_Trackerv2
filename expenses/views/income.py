from django.contrib.auth.decorators import login_required
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404

from expenses.forms import IncomeForm
from expenses.models import Income, User

from expenses.notifications import notify_user
from expenses.services import get_user_stats
from expenses.utils import get_int, get_selected_period, get_selected_user


@login_required
def list_income(request):

    users = User.objects.all()
    month_range = range(1,13)

    selected_user_id = get_selected_user(request)
    selected_user = get_object_or_404(User, id=selected_user_id)
    selected_month, selected_year = get_selected_period(request)

    income = Income.objects.filter(user=selected_user, date__month=selected_month, date__year=selected_year)
    context = {
        'users': users,
        'user_stats': get_user_stats(selected_user, selected_month, selected_year),
        'month_range': month_range,
        'incomes': income,
        'selected_user': selected_user,
        'selected_month': selected_month,
        'selected_year': selected_year,
    }
    return render(request, 'income/income_list.html', context)


@login_required
def add_income(request):


    current_user = request.user
    current_month, current_year = date.today().month, date.today().year

    incomes = Income.objects.filter(user=current_user, date__month=current_month, date__year=current_year)

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            new_income = form.save(commit=False)
            new_income.user = current_user
            new_income.save()

            user_stats = get_user_stats(current_user, date.today().month, date.today().year)

            notify_user(
                added_by_username=request.user.username,
                amount=new_income.amount,
                category="Income",
                description=new_income.description,
                budget=user_stats['net_balance'],
            )

            return redirect('add_income')
    else:
        form = IncomeForm()

    context = {
        'form': form,
        'current_month': date.today().strftime("%B"),
        'user_stats': get_user_stats(current_user, current_month, current_year),
        'incomes': incomes,

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
