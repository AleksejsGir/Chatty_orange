# users/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import CustomUser


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()  # Используем get_user_model() напрямую
        fields = ['username', 'email', 'bio', 'contacts', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contacts': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if get_user_model().objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError("Это имя пользователя уже занято.")
        return username