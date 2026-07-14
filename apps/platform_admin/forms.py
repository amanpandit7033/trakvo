from django import forms
from .models import PlatformPayment

class PlatformPaymentForm(forms.ModelForm):
    class Meta:
        model = PlatformPayment
        fields = ['amount', 'payment_date', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-ink/20'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-ink/20'}),
            'notes': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-ink/20'}),
        }

class ExtendTrialForm(forms.Form):
    trial_ends_on = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-ink/20'}))

from apps.accounts.models import CustomUser

class InstituteCreationForm(forms.Form):
    institute_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-ink/20'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-ink/20', 'placeholder': 'e.g. Patna, Gopalganj'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-ink/20'}))
    institute_phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-ink/20'}))
    
    owner_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-ink/20'}))
    owner_phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-ink/20', 'placeholder': 'Used for owner login'}))
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-ink/20', 'placeholder': 'Leave blank to auto-generate'}))

    def clean_owner_phone_number(self):
        phone = self.cleaned_data['owner_phone_number']
        if CustomUser.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("This phone number is already registered to another user.")
        return phone
