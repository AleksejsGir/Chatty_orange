# subscriptions/urls.py
from django.urls import path
from . import views # Импортируем views, хотя их пока нет

app_name = 'subscriptions' # Определяем пространство имен URL

urlpatterns = [
    # Здесь будут URL-паттерны для подписок
    # path('feed/', views.feed, name='feed'), # Пример будущего пути
]

# <!-- TODO: Добавлять сюда URL-паттерны для приложения subscriptions по мере реализации views. -->