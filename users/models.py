# Copyright 2024-2025 Aleksejs Giruckis, Igor Pronin, Viktor Yerokhov,
# Maxim Schneider, Ivan Miakinnov, Eugen Maljas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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