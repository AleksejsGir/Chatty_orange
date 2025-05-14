# subscriptions/admin.py
from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('subscriber__username', 'author__username')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        # Разрешаем добавление только через интерфейс подписки
        return True

    def send_notifications(self, request, queryset):
        # Здесь можно добавить логику отправки уведомлений
        count = queryset.count()
        self.message_user(request, f"Уведомления отправлены {count} подписчикам")
    send_notifications.short_description = "Отправить уведомления выбранным подписчикам"