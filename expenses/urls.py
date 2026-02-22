from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.add_expense, name='add_expense'),
    path('records/', views.expense, name='records'),
    path('update/<int:id>', views.update_expense, name='update_expense'),
    path('delete/<int:id>', views.delete_expense, name='delete_expense'),
    path('user/', views.summary, name='summary'),
    path('income/add', views.add_income, name='add_income')
]