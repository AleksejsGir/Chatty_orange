from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import perform_login
from django.contrib.auth import get_user_model

User = get_user_model()


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Связывает социальный аккаунт с существующим пользователем
        если email совпадает
        """
        if sociallogin.is_existing:
            return

        if 'email' in sociallogin.account.extra_data:
            email = sociallogin.account.extra_data['email']
            try:
                user = User.objects.get(email__iexact=email)
                sociallogin.connect(request, user)
                # Автоматический вход без проверки email, так как Google уже проверил
                perform_login(request, user, email_verification='none')
            except User.DoesNotExist:
                pass