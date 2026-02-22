import datetime

from django import forms

from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category', 'date', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control color-2'}),
            'category': forms.Select(attrs={'class': 'form-select color-2'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control color-2'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control color-2',
                'rows': 1,
                'placeholder': 'if anything special..',
            }),
        }