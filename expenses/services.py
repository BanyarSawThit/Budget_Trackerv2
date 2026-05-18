import calendar
import datetime
from datetime import date
from decimal import Decimal

from django.db.models import Sum

from expenses.models import Income, Deposit, Expense, SHARED_CATEGORIES


def get_user_stats(user, month, year):

    """
    Calculate financial stats for a given user.

    :param user: User instance
    :param month: int
    :param year: int
    :return: dict with keys:
        - income : total income for the month
        - deposit : total deposit of shared pool
        - total_budget : (income - deposit) total budget left
        - personal_ex : personal spending
        - personal_budget : total budget - personal_ex
    """

    income = (Income.objects
              .filter(user=user, date__month=month, date__year=year)
              .aggregate(Sum("amount"))["amount__sum"] or 0)

    deposit = (Deposit.objects
               .filter(user=user, date__month=month, date__year=year)
               .aggregate(Sum("amount"))["amount__sum"] or 0)

    expenses = (Expense.objects
                .filter(user=user, date__month=month, date__year=year)
                .exclude(category__in=SHARED_CATEGORIES)
                .aggregate(Sum("amount"))["amount__sum"] or 0)

    all_income = (Income.objects.filter(user=user)
              .aggregate(Sum("amount"))["amount__sum"] or 0)
    all_deposit = (Deposit.objects.filter(user=user)
               .aggregate(Sum("amount"))["amount__sum"] or 0)
    all_expenses = (Expense.objects.filter(user=user)
                .exclude(category__in=SHARED_CATEGORIES)
                .aggregate(Sum("amount"))["amount__sum"] or 0)

    today = date.today()
    if month == today.month and year == today.year:
        days_in_month = Decimal(today.day)
    else:
        days_in_month = Decimal(calendar.monthrange(year, month)[1])

    balance = all_income - all_deposit - all_expenses
    daily_expense_avg = expenses / days_in_month


    return {
        'income': income,
        'deposit': deposit,
        'personal_ex': expenses,
        'net_balance': balance,
        'daily_expense_avg': daily_expense_avg,
    }

def get_deposit(month, year):


    deposit = (Deposit.objects.filter(date__month=month, date__year=year)
               .aggregate(Sum("amount"))["amount__sum"] or 0)

    shared_spent = (Expense.objects.filter(category__in=SHARED_CATEGORIES, date__month=month, date__year=year)
                    .aggregate(Sum("amount"))["amount__sum"] or 0)

    return deposit - shared_spent

def get_opening_budget(user, month, year):

    start_of_month = datetime.date(year, month, 1)

    income = Income.objects.filter(user=user, date__lt=start_of_month).aggregate(Sum("amount"))["amount__sum"] or 0
    deposit = Deposit.objects.filter(user=user, date__lt=start_of_month).aggregate(Sum("amount"))["amount__sum"] or 0
    expenses = Expense.objects.filter(user=user, date__lt=start_of_month).exclude(category__in=SHARED_CATEGORIES).aggregate(Sum("amount"))["amount__sum"] or 0

    return income - deposit - expenses

def get_shared_expenses(month, year):

    shared_expense = (Expense.objects.filter(category__in=SHARED_CATEGORIES, date__month=month, date__year=year))

    shared_food = shared_expense.filter(category='food').aggregate(Sum('amount'))['amount__sum'] or 0
    shared_grocery = shared_expense.filter(category='grocery').aggregate(Sum('amount'))['amount__sum'] or 0
    shared_utility = shared_expense.filter(category='utility').aggregate(Sum('amount'))['amount__sum'] or 0

    return shared_food, shared_grocery, shared_utility