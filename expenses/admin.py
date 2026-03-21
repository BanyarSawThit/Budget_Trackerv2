from django.contrib import admin

from . import models

# Register your models here.
@admin.register(models.Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['date', 'user', 'category', 'amount', 'description']

@admin.register(models.Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['date', 'user', 'amount', 'description']

@admin.register(models.Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ['date', 'user', 'amount',  'description']

@admin.register(models.ShoppingItem)
class ShoppingAdmin(admin.ModelAdmin):
    list_display = ['item']

