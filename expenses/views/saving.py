from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from expenses.forms import SavingForm
from expenses.models import Saving
from expenses.services import get_saving
from expenses.utils import get_selected_user, get_selected_period


@login_required
def add_saving(request):

    current_user = request.user
    current_month, current_year = date.today().month, date.today().year

    saving = Saving.objects.filter(user=current_user, date__month=current_month, date__year=current_year)

    total_saving = get_saving(current_user)

    if request.method == 'POST':
        form = SavingForm(request.POST)
        if form.is_valid():
            new_saving = form.save(commit=False)
            new_saving.user = current_user
            new_saving.save()

            return redirect('add_saving')
    else:
        form = SavingForm()

    context = {
        'current_month': date.today().strftime("%B"),
        'form': form,
        'saving': saving,
        'total_saving': total_saving,
    }
    return render(request, 'saving/add_saving.html', context)

@login_required
def list_saving(request):

    users = User.objects.all()
    selected_user = get_selected_user(request)
    selected_month, selected_year = get_selected_period(request)
    month_range = range(1, 13)

    savings = (Saving.objects.filter(user=selected_user, date__month=selected_month, date__year=selected_year))

    saving_total = (savings.aggregate(Sum('amount'))['amount__sum'] or 0)


    context = {
        'users': users,
        'month_range': month_range,

        'savings': savings,
        'saving_total': saving_total,

        'selected_user': selected_user,
        'selected_month': selected_month,
        'selected_year': selected_year,
    }
    return render(request, 'saving/saving_list.html', context)


@login_required
def edit_saving(request, id):
     saving = get_object_or_404(Saving, id=id, user=request.user)

     if request.method == 'POST':
         form = SavingForm(request.POST, instance=saving)
         if form.is_valid():
             form.save()
             return redirect('add_saving')

     else:
         form = SavingForm(instance=saving)
     return render(request, 'saving/edit_saving.html', {'form': form, 'item': saving})


@login_required
def delete_saving(request, id):
    saving = get_object_or_404(Saving, id=id, user=request.user)

    if request.method == 'POST':
        saving.delete()
        return redirect('add_saving')

    return render(request, 'saving/delete_saving.html', {'item': saving})