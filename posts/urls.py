# posts/urls.py
from django.urls import path
from . import views # Импортируем views, хотя их пока нет
# posts/urls.py
from django.urls import path
from . import views

app_name = 'posts' # Определяем пространство имен URL


urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
]


# urlpatterns = [
    # Здесь будут URL-паттерны для постов
    # path('', views.post_list, name='list'), # Пример будущего пути
# ]

# <!-- TODO: Добавлять сюда URL-паттерны для приложения posts по мере реализации views. -->