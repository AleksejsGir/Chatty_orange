# users/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import CustomUser
from allauth.account.forms import SignupForm

# users/forms.py
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'bio', 'contacts', 'avatar']  # username должен быть в fields

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Проверка на уникальность (исключая текущего пользователя)
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(username__iexact=username).exists():
            raise forms.ValidationError("Это имя пользователя уже занято.")
        return username

class CustomSignupForm(SignupForm):
    # agree_to_terms = forms.BooleanField(
    #     label="Я согласен с условиями использования",
    #     required=True,
    #     error_messages={'required': 'Вы должны принять условия использования'}
    # )

    def save(self, request):
        user = super().save(request)
        user.agree_to_terms = self.cleaned_data['agree_to_terms']
        user.save()
        return user