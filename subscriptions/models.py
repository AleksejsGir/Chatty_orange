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