# expenses/models
from datetime import datetime

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
        ('fun', 'Fun & Snack')
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
    date = models.DateField(default=datetime.today)
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
    date = models.DateField(default=datetime.today)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.date}"


class Deposit(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    date = models.DateField(default=datetime.today)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} deposited {self.amount} on {self.date}"