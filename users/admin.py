from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'bio')
    ordering = ('username',)
    date_hierarchy = 'date_joined'

    # Добавляем наши поля в fieldsets
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Личная информация", {"fields": ("first_name", "last_name", "email", "bio", "contacts", "avatar")}),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    readonly_fields = ('date_joined', 'last_login')

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = "Количество постов"

    # Добавляем действие для блокировки пользователей
    actions = ['block_users', 'unblock_users']

    def block_users(self, request, queryset):
        queryset.update(is_active=False)

    block_users.short_description = "Заблокировать выбранных пользователей"

    def unblock_users(self, request, queryset):
        queryset.update(is_active=True)

    unblock_users.short_description = "Разблокировать выбранных пользователей"
