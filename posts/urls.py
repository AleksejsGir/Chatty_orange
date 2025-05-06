# posts/urls.py
from django.urls import path
from . import views # Импортируем views, хотя их пока нет
from .views import (
    PostCreateView,
    PostListView,
    PostDetailView,
    # PostUpdateView,
    # PostDeleteView
)

app_name = 'posts' # Определяем пространство имен URL

urlpatterns = [
    # # Здесь будут URL-паттерны для постов
    # path('', views.post_list, name='list'), # Пример будущего пути
    path('', PostListView.as_view(), name='post_list'),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    # path('<slug:slug>/update/', PostUpdateView.as_view(), name='post_update'),
    # path('<slug:slug>/delete/', PostDeleteView.as_view(), name='post_delete'),
]

# <!-- TODO: Добавлять сюда URL-паттерны для приложения posts по мере реализации views. -->