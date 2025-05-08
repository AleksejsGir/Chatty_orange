# subscriptions/models.py
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
        auto_now_add=True,
        verbose_name="Дата подписки"
    )

    def __str__(self):
        return f"{self.subscriber} подписан на {self.author}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ('subscriber', 'author')  # Запрещаем повторные подписки
        ordering = ["-created_at"]