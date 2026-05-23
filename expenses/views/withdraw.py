from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from expenses.forms import WithdrawForm
from expenses.models import SavingWithdrawal as Withdraw
from expenses.services import get_saving
from expenses.utils import get_selected_user, get_selected_period


@login_required
def add_withdraw(request):

    current_user = request.user
    current_month, current_year = date.today().month, date.today().year

    withdrawals = Withdraw.objects.filter(
        user=current_user,
        date__month=current_month,
        date__year=current_year,
    )

    total_saving = get_saving(current_user)

    if request.method == 'POST':
        form = WithdrawForm(request.POST)
        if form.is_valid():
            withdraw = form.save(commit=False)
            withdraw.user = current_user
            withdraw.save()
            return redirect('add_withdraw')
    else:
        form = WithdrawForm()

    context = {
        'current_month': date.today().strftime("%B"),
        'form': form,
        'withdrawals': withdrawals,
        'total_saving': total_saving,
    }
    return render(request, 'withdraw/add_withdraw.html', context)


@login_required
def list_withdraw(request):

    users = User.objects.all()
    selected_user_id = get_selected_user(request)
    selected_month, selected_year = get_selected_period(request)
    month_range = range(1, 13)

    withdrawals = Withdraw.objects.filter(
        user_id=selected_user_id,
        date__month=selected_month,
        date__year=selected_year,
    )

    withdraw_total = withdrawals.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'users': users,
        'month_range': month_range,

        'withdrawals': withdrawals,
        'withdraw_total': withdraw_total,

        'selected_user': selected_user_id,
        'selected_month': selected_month,
        'selected_year': selected_year,
    }
    return render(request, 'withdraw/withdraw_list.html', context)


@login_required
def edit_withdraw(request, id):
    withdraw = get_object_or_404(Withdraw, id=id, user=request.user)

    if request.method == 'POST':
        form = WithdrawForm(request.POST, instance=withdraw)
        if form.is_valid():
            form.save()
            return redirect('add_withdraw')
    else:
        form = WithdrawForm(instance=withdraw)

    return render(request, 'withdraw/edit_withdraw.html', {'form': form, 'item': withdraw})


@login_required
def delete_withdraw(request, id):
    withdraw = get_object_or_404(Withdraw, id=id, user=request.user)

    if request.method == 'POST':
        withdraw.delete()
        return redirect('add_withdraw')

    return render(request, 'withdraw/delete_withdraw.html', {'item': withdraw})