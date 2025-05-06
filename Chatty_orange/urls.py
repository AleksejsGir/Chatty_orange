# Chatty_orange/urls.py
from django.contrib import admin
from django.urls import path, include
from users import views as user_views # Импортируем views из приложения users

urlpatterns = [
    # Главная страница
    path('', user_views.home_page_view, name='home'), # Добавлен путь для главной страницы

    # Админка
    path('admin/', admin.site.urls),

    # Приложения
    path('users/', include('users.urls', namespace='users')),
    path('posts/', include('posts.urls', namespace='posts')),
    path('subscriptions/', include('subscriptions.urls', namespace='subscriptions')),
    path('accounts/', include('allauth.urls')),
]


# <!-- TODO: Настроить раздачу медиафайлов в режиме DEBUG (если необходимо). -->
# <!-- TODO: Подключить URL для django-debug-toolbar (если используется). -->