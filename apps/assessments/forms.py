from django import forms
from .models import Test
from apps.institutes.models import Batch

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['batch', 'name', 'test_date', 'max_marks']
        widgets = {
            'batch': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-blue outline-none bg-white'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-blue outline-none', 'placeholder': 'e.g. Unit Test 1'}),
            'test_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-blue outline-none'}),
            'max_marks': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-brand-blue outline-none', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        institute = kwargs.pop('institute', None)
        super().__init__(*args, **kwargs)
        if institute:
            self.fields['batch'].queryset = Batch.objects.filter(institute=institute)
