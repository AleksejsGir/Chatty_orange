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


from django.db import models
from django.conf import settings
from django.utils import timezone

class Subscription(models.Model):
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата подписки"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        # Уникальное сочетание подписчика и автора, чтобы избежать дублирования
        unique_together = ['subscriber', 'author']
        ordering = ['-created_at']  # От новых к старым

    def __str__(self):
        return f"{self.subscriber.username} → {self.author.username}"