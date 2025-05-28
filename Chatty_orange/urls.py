# Chatty_orange/urls.py
from django.conf import settings # Импортируем settings здесь, а не из Chatty_orange
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

# Для home_page_view
from users import views as user_views

# Для TermsOfUseView и PrivacyPolicyView - ПРЕДПОЛОЖИМ, что они в posts.views
# Если они в другом месте (например, users.views или core.views), измените импорт
from posts import views as post_views # Переименуем для ясности, если home_page_view из users.views

urlpatterns = [
    path('admin/', admin.site.urls), # Django автоматически присваивает namespace 'admin'

    # Главная страница
    path('', user_views.home_page_view, name='home'),

    # Приложения с пространствами имен
    path('users/', include('users.urls', namespace='users')),
    path('posts/', include('posts.urls', namespace='posts')),
    path('subscriptions/', include('subscriptions.urls', namespace='subscriptions')),
    path('accounts/', include('allauth.urls')), # allauth сам управляет своими пространствами имен

    # Статические страницы (условия использования и политика конфиденциальности)
    path('terms/', post_views.TermsOfUseView.as_view(), name='terms-of-use'),
    path('privacy/', post_views.PrivacyPolicyView.as_view(), name='privacy-policy'),
    # path('feedback/', include('feedback.urls')),

    # Debug Toolbar (если используется, подключаем в конце и только в DEBUG)
    # Эта часть будет добавлена ниже, внутри if settings.DEBUG
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Добавляем URL для Debug Toolbar только в режиме DEBUG
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
