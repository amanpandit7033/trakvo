from django import forms
from .models import Institute, Batch

class InstituteForm(forms.ModelForm):
    class Meta:
        model = Institute
        fields = ['name', 'logo', 'address', 'city', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass outline-none transition-all text-brand-ink'}),
            'logo': forms.FileInput(attrs={'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border file:border-brand-hairline file:text-sm file:font-medium file:bg-brand-paper file:text-brand-ink hover:file:brightness-95'}),
            'address': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass outline-none transition-all text-brand-ink'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass outline-none transition-all text-brand-ink'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass outline-none transition-all text-brand-ink'}),
        }

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass outline-none transition-all text-brand-ink'}),
            'description': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass outline-none transition-all text-brand-ink'}),
        }
