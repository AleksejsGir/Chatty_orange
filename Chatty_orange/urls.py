# Chatty_orange/urls.py
from django.contrib import admin
from django.urls import path, include # Убедитесь, что include импортирован

urlpatterns = [
    path('admin/', admin.site.urls),
    # Подключаем URL-адреса из приложений:
    path('users/', include('users.urls', namespace='users')), # Добавляем namespace='users'
    path('posts/', include('posts.urls', namespace='posts')), # Добавляем namespace='posts'
    path('subscriptions/', include('subscriptions.urls', namespace='subscriptions')), # Добавляем namespace='subscriptions'

    # TODO: Добавить путь для главной страницы ('') позже
    # path('', views.home_page, name='home'),
]

# <!-- TODO: Добавить URL для главной страницы. -->
# <!-- TODO: Настроить раздачу медиафайлов в режиме DEBUG (если необходимо). -->
# <!-- TODO: Подключить URL для django-debug-toolbar (если используется). -->