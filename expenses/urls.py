from django.urls import path, include

from .views import deposit, expense, income, shopping

urlpatterns = [
    #expense
    path('expense/', expense.expense_list, name='expense_list'),
    path('', expense.add_expense, name='add_expense'),
    path('edit/<int:id>', expense.edit_expense, name='edit_expense'),
    path('delete/<int:id>', expense.delete_expense, name='delete_expense'),

    # income
    path('income/', income.list_income, name='income_list'),
    path('income/add/', income.add_income, name='add_income'),
    path('income/edit/<int:id>', income.edit_income, name='edit_income'),
    path('income/delete/<int:id>', income.delete_income, name='delete_income'),

    # deposit
    path('deposit/', deposit.list_deposit, name='deposit_list'),
    path('deposit/add/', deposit.add_deposit, name='add_deposit'),
    path('deposit/edit/<int:id>', deposit.edit_deposit, name='edit_deposit'),
    path('deposit/delete/<int:id>', deposit.delete_deposit, name='delete_deposit'),

    # summary
    path('summary/', expense.summary, name='summary'),
    path('user/', expense.user_detail, name='user_detail'),
    path('user/<int:user_id>', expense.user_detail, name='user_detail_by_id'),

    # export
    path('export/expenses', expense.export_expense_csv, name='expose_expense'),

    # shopping list
    path('shopping/', shopping.shopping_view, name='shopping_page'),

]