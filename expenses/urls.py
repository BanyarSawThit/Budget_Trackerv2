from django.urls import path, include

from . import views

urlpatterns = [
    #expense
    path('expense/', views.expense_list, name='expense_list'),
    path('', views.add_expense, name='add_expense'),
    path('edit/<int:id>', views.edit_expense, name='edit_expense'),
    path('delete/<int:id>', views.delete_expense, name='delete_expense'),

    # income
    path('income/', views.list_income, name='income_list'),
    path('income/add/', views.add_income, name='add_income'),
    path('income/edit/<int:id>', views.edit_income, name='edit_income'),
    path('income/delete/<int:id>', views.delete_income, name='delete_income'),

    # deposit
    path('deposit/', views.list_deposit, name='deposit_list'),
    path('deposit/add/', views.add_deposit, name='add_deposit'),
    path('deposit/edit/<int:id>', views.edit_deposit, name='edit_deposit'),
    path('deposit/delete/<int:id>', views.delete_deposit, name='delete_deposit'),

    # user summary
    path('user/', views.summary, name='summary'),

    path('export/expenses', views.export_expense_csv, name='expose_expense'),
    path('export/all/', views.export_all_csv, name='export_all_csv'),

]