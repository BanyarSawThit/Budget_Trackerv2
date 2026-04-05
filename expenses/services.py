from datetime import date

from django.db.models import Sum

from expenses.models import Income, Deposit, Expense, SHARED_CATEGORIES


def get_user_stats(user, month, year):

    income_amount = (Income.objects
                     .filter(user=user, date__month=month, date__year=year)
                     .aggregate(Sum("amount"))["amount__sum"] or 0)

    deposit_amount = (Deposit.objects
                      .filter(user=user, date__month=month, date__year=year)
                      .aggregate(Sum("amount"))["amount__sum"] or 0)

    expense_amount = (Expense.objects
                      .filter(user=user, date__month=month, date__year=year)
                      .exclude(category__in=SHARED_CATEGORIES)
                      .aggregate(Sum("amount"))["amount__sum"] or 0)

    total_budget_amount = income_amount - deposit_amount
    budget_left_amount = income_amount - deposit_amount - expense_amount

    return {
        'income': income_amount,
        'deposit': deposit_amount,
        'total_budget': total_budget_amount,
        'personal_ex': expense_amount,
        'budget_left': budget_left_amount,
    }