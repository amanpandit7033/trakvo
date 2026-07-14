from django import forms
from .models import FeeStructure, Payment

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['total_amount', 'due_date', 'installment_label']
        widgets = {
            'total_amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-blue outline-none', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-blue outline-none'}),
            'installment_label': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-blue outline-none', 'placeholder': 'e.g. Month 1, Term 1'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'payment_mode', 'notes']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-blue outline-none', 'step': '0.01'}),
            'payment_mode': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-blue outline-none bg-white'}),
            'notes': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-blue outline-none', 'placeholder': 'Optional details like UPI ID'}),
        }
