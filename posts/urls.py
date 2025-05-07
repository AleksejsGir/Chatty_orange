# posts/urls.py
from django.urls import path
from . import views # Импортируем views, хотя их пока нет

app_name = 'posts' # Определяем пространство имен URL

urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('create/', views.PostCreateView.as_view(), name='post-create'),
    path('<int:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    # Здесь будут URL-паттерны для постов
    # path('', views.post_list, name='list'), # Пример будущего пути
]

# <!-- TODO: Добавлять сюда URL-паттерны для приложения posts по мере реализации views. -->