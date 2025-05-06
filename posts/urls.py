# posts/urls.py
from django.urls import path
from . import views # Импортируем views, хотя их пока нет

app_name = 'posts' # Определяем пространство имен URL

urlpatterns = [
    # Здесь будут URL-паттерны для постов
    path('', views.post_list, name='list'), # Пример будущего пути
]

# <!-- TODO: Добавлять сюда URL-паттерны для приложения posts по мере реализации views. -->