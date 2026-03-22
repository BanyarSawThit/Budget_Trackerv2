from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def set_currency(request):
    """
    Store chosen currency in session

    :param request:
    :return:
    """
    selected_currency = request.POST.get('currency', 'THB')
    if selected_currency not in ['THB', 'MMK']:
        selected_currency = 'THB'

    request.session['currency'] = selected_currency

    return redirect(request.POST.get('next', '/'))
