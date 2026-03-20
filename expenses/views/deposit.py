from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from expenses.forms import DepositForm
from expenses.models import Deposit
from expenses.notifications import notify_other_user


@login_required
def list_deposit(request):
    deposit = Deposit.objects.select_related('user').all()

    deposit_data = {}

    for item in deposit:
        deposit_data[item.id] = {
            'id': item.id,
            'user': item.user,
            'amount': item.amount,
            'date': item.date,
            'description': item.description
        }

    context = {
        'deposit_data': deposit_data,
    }
    return render(request, 'expenses/deposit_list.html', context)


@login_required
def add_deposit(request):
    deposit = Deposit.objects.select_related('user').all()
    current_month_deposit_amount = (deposit
                         .filter(date__month=date.today().month,
                                 date__year=date.today().year)
                         .aggregate(Sum('amount'))['amount__sum'] or 0)
    current_month_deposit_list = deposit.filter(date__month=date.today().month,
                                                date__year=date.today().year)

    deposit_data = {}

    for item in current_month_deposit_list:
        deposit_data[item.id] = {
            'id': item.id,
            'user': item.user,
            'amount': item.amount,
            'date': item.date,
            'description': item.description
        }

    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.user = request.user
            deposit.save()

            notify_other_user(
                added_by_username=request.user.username,
                amount=deposit.amount,
                category="Deposit",
                description=deposit.description
            )

            return redirect('add_deposit')
    else:
        form = DepositForm()

    context = {
        'form': form,
        'current_month': date.today().strftime("%B"),
        'current_month_deposit_amount': current_month_deposit_amount,
        'deposit_data': deposit_data,
    }
    return render(request, 'expenses/add_deposit.html', context)


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
    return render(request, 'expenses/edit_deposit.html', {'form': form, 'item': deposit_item})


@login_required
def delete_deposit(request, id):
    deposit_item = get_object_or_404(Deposit, id=id, user=request.user)

    if request.method == 'POST':
        deposit_item.delete()
        return redirect('add_deposit')

    return render(request, 'expenses/delete_deposit.html', {'item': deposit_item})
