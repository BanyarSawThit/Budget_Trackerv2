from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from expenses.forms import DepositForm
from expenses.models import Deposit, User
from expenses.notifications import notify_user
from expenses.services import get_user_stats
from expenses.utils import get_int, get_selected_period, get_selected_user


@login_required
def list_deposit(request):

    users = User.objects.all()
    month_range = range(1,13)

    selected_user = get_selected_user(request)
    selected_month, selected_year = get_selected_period(request)

    deposits = Deposit.objects.filter(user=selected_user, date__month=selected_month, date__year=selected_year)

    context = {
        'users': users,
        'month_range': month_range,
        'user_stats': get_user_stats(selected_user, selected_month, selected_year),
        'deposits': deposits,
        'selected_user': selected_user,
        'selected_month': selected_month,
        'selected_year': selected_year,
    }
    return render(request, 'deposit/deposit_list.html', context)


@login_required
def add_deposit(request):

    current_user = request.user
    current_month, current_year = date.today().month, date.today().year

    deposits = Deposit.objects.filter(user=current_user, date__month=current_month, date__year=current_year)

    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            new_deposit = form.save(commit=False)
            new_deposit.user = current_user
            new_deposit.save()

            # Get user budget
            user_stats = get_user_stats(current_user, current_month, current_year)

            notify_user(
                added_by_username=request.user.username,
                amount=new_deposit.amount,
                category="Deposit",
                description=new_deposit.description,
                budget=user_stats['net_balance'],
            )

            return redirect('add_deposit')
    else:
        form = DepositForm()

    context = {
        'form': form,
        'current_month': date.today().strftime("%B"),
        'user_stats': get_user_stats(current_user, current_month, current_year),
        'deposits': deposits,
    }
    return render(request, 'deposit/add_deposit.html', context)


@login_required
def edit_deposit(request, id):
    deposit_item = get_object_or_404(Deposit, id=id, user=request.user)
    if request.method == 'POST':
        form = DepositForm(request.POST, instance=deposit_item)
        if form.is_valid():
            form.save()
            return redirect('add_deposit')
    else:
        form = DepositForm(instance=deposit_item)
    return render(request, 'deposit/edit_deposit.html', {'form': form, 'item': deposit_item})


@login_required
def delete_deposit(request, id):
    deposit_item = get_object_or_404(Deposit, id=id, user=request.user)

    if request.method == 'POST':
        deposit_item.delete()
        return redirect('add_deposit')

    return render(request, 'deposit/delete_deposit.html', {'item': deposit_item})
