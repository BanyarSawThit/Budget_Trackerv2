import calendar
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


    started_income = (Income.objects
                     .filter(user=user)
                     .exclude(date__month=month, date__year=year)
                     .aggregate(Sum("amount"))["amount__sum"] or 0)

    started_deposit = (Deposit.objects
                      .filter(user=user)
                      .exclude(date__month=month, date__year=year)
                      .aggregate(Sum("amount"))["amount__sum"] or 0)

    started_expenses = (Expense.objects
                      .filter(user=user)
                      .exclude(category__in=SHARED_CATEGORIES, date__month=month, date__year=year)
                      .aggregate(Sum("amount"))["amount__sum"] or 0)

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

    # print(started_income, started_deposit, started_expenses)
    # started_budget = started_income - started_deposit - started_expenses
    balance = all_income - all_deposit - all_expenses
    daily_expense_avg = expenses / days_in_month


    return {
        'income': income,
        'deposit': deposit,
        # 'started_budget': started_budget,
        'personal_ex': expenses,
        'balance': balance,
        'daily_expense_avg': daily_expense_avg,
    }

def get_available_balance(user):

    """
    Calculate the balance of a given user.

    :param user: User instance
    :return: int - balance amount
    """
    income = (Income.objects.filter(user=user)
              .aggregate(Sum("amount"))["amount__sum"] or 0)
    deposit = (Deposit.objects.filter(user=user)
              .aggregate(Sum("amount"))["amount__sum"] or 0)
    expenses = (Expense.objects.filter(user=user)
                .exclude(category__in=SHARED_CATEGORIES)
                .aggregate(Sum("amount"))["amount__sum"] or 0)

    balance = income - deposit - expenses

    return balance