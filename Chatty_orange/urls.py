# Chatty_orange/urls.py
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from Chatty_orange import settings
from posts import views
from users import views as user_views  # Импортируем views из приложения users

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('users/', include('users.urls')),
    # path('posts/', include('posts.urls')),
    # Главная страница
    path('', user_views.home_page_view, name='home'),  # Добавлен путь для главной страницы

    # Админка
    path('admin/', admin.site.urls),

    # Приложения
    path('users/', include('users.urls', namespace='users')),
    path('posts/', include('posts.urls', namespace='posts')),
    path('subscriptions/', include('subscriptions.urls', namespace='subscriptions')),
    path('accounts/', include('allauth.urls')),

    # Просмотр условий использования и политики конфиденциальности
    path('terms/', views.TermsOfUseView.as_view(), name='terms-of-use'),
    path('privacy/', views.PrivacyPolicyView.as_view(), name='privacy-policy'),
    # path('feedback/', include('feedback.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



# <!-- TODO: Настроить раздачу медиафайлов в режиме DEBUG (если необходимо). -->
# <!-- TODO: Подключить URL для django-debug-toolbar (если используется). -->