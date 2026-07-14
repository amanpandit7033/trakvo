from django import forms
from .models import Student
from apps.institutes.models import Batch

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'phone_number', 'parent_name', 'parent_phone_number', 'date_of_birth', 'batch']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass focus:border-transparent outline-none transition-all'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass focus:border-transparent outline-none transition-all'}),
            'parent_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass focus:border-transparent outline-none transition-all'}),
            'parent_phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass focus:border-transparent outline-none transition-all'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass focus:border-transparent outline-none transition-all'}),
            'batch': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass focus:border-transparent outline-none transition-all bg-white'}),
        }

    def __init__(self, *args, **kwargs):
        institute = kwargs.pop('institute', None)
        super().__init__(*args, **kwargs)
        if institute:
            self.fields['batch'].queryset = Batch.objects.filter(institute=institute)
