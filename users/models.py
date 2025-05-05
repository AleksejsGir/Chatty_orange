# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    bio = models.TextField(_("О себе"), max_length=500, blank=True, null=True)
    contacts = models.CharField(_("Контакты"), max_length=200, blank=True, null=True)
    avatar = models.ImageField(_("Аватар"), upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        # Предполагаем, что URL профиля будет иметь имя 'profile' в пространстве 'users'
        # и принимать 'username' как параметр
        return reverse('users:profile', kwargs={'username': self.username})

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ['username']