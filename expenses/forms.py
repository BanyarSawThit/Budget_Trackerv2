from django import forms

from .models import Expense, Income, Deposit, ShoppingItem


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category','description', 'date',]
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': '---\n---',
            }),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0")
        return amount


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'description', 'date']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': 'From...',
            })
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0")
        return amount


class DepositForm(forms.ModelForm):
    class Meta:
        model = Deposit
        fields = ['amount', 'description', 'date']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': 'Note...',
            })
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0")
        return amount

class ShoppingForm(forms.ModelForm):
    class Meta:
        model = ShoppingItem
        fields = ['item']
        labels = {
            'item': ''
        }
        widgets = {
            'item': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': '1. ...\n2. ...',
            }),
        }