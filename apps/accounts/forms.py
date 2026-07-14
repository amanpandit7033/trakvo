from django import forms
from .models import CustomUser

class TeacherCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass outline-none transition-all text-brand-ink'
        }),
        label="Temporary Password"
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass outline-none transition-all text-brand-ink'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass outline-none transition-all text-brand-ink'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-brand-hairline rounded-lg focus:ring-2 focus:ring-brand-brass outline-none transition-all text-brand-ink', 'placeholder': 'e.g., +1234567890'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
