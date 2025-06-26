from django.db import models
from django.conf import settings
from django.utils import timezone

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_messages',
        on_delete=models.CASCADE,
        verbose_name='Отправитель'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_messages',
        on_delete=models.CASCADE,
        verbose_name='Получатель'
    )
    text = models.TextField('Текст сообщения')
    timestamp = models.DateTimeField('Дата и время', default=timezone.now)
    is_read = models.BooleanField('Прочитано', default=False)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f'От {self.sender} к {self.recipient}: {self.text[:20]}'


