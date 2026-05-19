# expenses/models
from datetime import date

from django.db import models
from django.contrib.auth.models import User


CATEGORY_CHOICES = [
    ('food', 'Food*'),
    ('drink', 'Drink'),
    ('commute', 'Commute'),
    ('grocery', 'Grocery*'),
    ('utility', 'Utility*'),
    ('wear', 'Wear'),
    ('cosmetic', 'Cosmetic'),
    ('fun', 'Fun & Snack'),
    ('gift', 'Gift'),
    ('others', 'Others')
                    ]

SHARED_CATEGORIES = ['food', 'grocery', 'utility']


class Expense(models.Model):
    """Store amount with category and date"""
    objects = models.Manager()
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default='food'
    )
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', '-created_at']

    @property
    def expense_type(self):
        return 'shared' if self.category in SHARED_CATEGORIES else 'personal'

    def __str__(self):
        return f"{self.user}: {self.expense_type} {self.category}: {self.amount} on {self.date}"


class Income(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    description = models.TextField(blank=True)
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.date}"


class Deposit(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    date = models.DateField(default=date.today)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} deposited {self.amount} on {self.date}"


class ShoppingItem(models.Model):
    item =  models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.item


class SavingGoal(models.Model):
    objects = models.Manager()

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=10, decimal_places=0)
    monthly_target = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.description}"
    

class Saving(models.Model):
    objects = models.Manager()

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal = models.ForeignKey(SavingGoal, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    date = models.DateField(default=date.today)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} saved {self.amount} on {self.date}"


class SavingWithdrawal(models.Model):
    objects = models.Manager()

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal = models.ForeignKey(SavingGoal, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    date = models.DateField(default=date.today)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} withdrew {self.amount} on {self.date}"


