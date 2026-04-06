import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

User = get_user_model()


@pytest.fixture
def google_social_app():
    """Создает SocialApp для Google в тестах."""
    app = SocialApp.objects.create(
        provider='google',
        name='Google',
        client_id='fake-client-id-for-tests',
        secret='fake-secret-for-tests',
    )
    # Привязываем к текущему сайту
    site = Site.objects.get_current()
    app.sites.add(site)
    return app


@pytest.mark.django_db
class TestUserViews:
    """Тесты для представлений пользователей."""

    def test_home_page_view(self, client):
        """Тест главной страницы."""
        url = reverse('home')
        response = client.get(url)
        assert response.status_code == 200
        assert 'Chatty' in response.content.decode()

    def test_profile_view(self, client, user):
        """Тест страницы профиля."""
        url = reverse('users:profile', kwargs={'username': user.username})
        response = client.get(url)
        assert response.status_code == 200
        assert user.username in response.content.decode()

    def test_profile_view_nonexistent_user(self, client):
        """Тест профиля несуществующего пользователя."""
        url = reverse('users:profile', kwargs={'username': 'nonexistent'})
        response = client.get(url)
        assert response.status_code == 404

    def test_profile_edit_view_authenticated(self, authenticated_client, user):
        """Тест редактирования профиля для авторизованного пользователя."""
        url = reverse('users:profile-edit', kwargs={'pk': user.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_profile_edit_view_unauthenticated(self, client, user):
        """Тест редактирования профиля для неавторизованного пользователя."""
        url = reverse('users:profile-edit', kwargs={'pk': user.pk})
        response = client.get(url)
        assert response.status_code == 302  # Редирект на страницу входа

    def test_profile_edit_view_wrong_user(self, authenticated_client, another_user):
        """Тест попытки редактирования чужого профиля."""
        url = reverse('users:profile-edit', kwargs={'pk': another_user.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 403  # Запрещено

    def test_profile_update_post(self, authenticated_client, user):
        """Тест обновления профиля."""
        url = reverse('users:profile-edit', kwargs={'pk': user.pk})
        data = {
            'username': 'updatedusername',
            'email': 'updated@example.com',
            'bio': 'Updated bio'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302  # Редирект после успешного обновления

        # Проверяем, что данные обновились
        user.refresh_from_db()
        assert user.username == 'updatedusername'
        assert user.email == 'updated@example.com'
        assert user.bio == 'Updated bio'


@pytest.mark.django_db
class TestAuthenticationViews:
    """Тесты для представлений аутентификации."""

    def test_login_view(self, client, google_social_app):
        """Тест страницы входа."""
        url = reverse('account_login')
        response = client.get(url)
        assert response.status_code == 200
        # Проверяем, что в ответе есть форма входа
        assert 'form' in response.context
        assert 'Вход' in response.content.decode() or 'Login' in response.content.decode()

    def test_signup_view(self, client, google_social_app):
        """Тест страницы регистрации."""
        url = reverse('account_signup')
        response = client.get(url)
        assert response.status_code == 200
        # Проверяем, что в ответе есть форма регистрации
        assert 'form' in response.context
        assert 'Регистрация' in response.content.decode() or 'Sign Up' in response.content.decode()

    def test_logout_view(self, authenticated_client):
        """Тест выхода из системы."""
        url = reverse('account_logout')
        response = authenticated_client.get(url)
        assert response.status_code == 200  # Показывает страницу подтверждения

    def test_login_with_valid_credentials(self, client, user, google_social_app):
        """Тест входа с правильными данными."""
        url = reverse('account_login')
        data = {
            'login': user.email,
            'password': 'testpass123'
        }
        response = client.post(url, data)
        # Должен быть редирект после успешного входа
        assert response.status_code == 302

    def test_signup_with_valid_data(self, client, google_social_app):
        """Тест регистрации с правильными данными."""
        url = reverse('account_signup')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        response = client.post(url, data)
        # Должен быть редирект после успешной регистрации
        assert response.status_code == 302

        # Проверяем, что пользователь создался
        assert User.objects.filter(username='newuser').exists()

    def test_signup_with_mismatched_passwords(self, client, google_social_app):
        """Тест регистрации с несовпадающими паролями."""
        url = reverse('account_signup')
        data = {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password1': 'complexpassword123',
            'password2': 'differentpassword123'
        }
        response = client.post(url, data)
        # Форма должна вернуться с ошибками
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    def test_login_with_invalid_credentials(self, client, google_social_app):
        """Тест входа с неправильными данными."""
        url = reverse('account_login')
        data = {
            'login': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        response = client.post(url, data)
        # Форма должна вернуться с ошибками
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors