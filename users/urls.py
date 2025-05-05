# users/urls.py
from django.urls import path
from . import views # Импортируем views

app_name = 'users' # Определяем пространство имен URL для приложения users

urlpatterns = [
    # Здесь будут URL-паттерны для пользователей:
    # path('register/', views.register, name='register'),
    # path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
]

# <!-- TODO: Добавлять сюда URL-паттерны для приложения users по мере реализации views. -->