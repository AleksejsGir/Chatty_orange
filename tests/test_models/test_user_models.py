import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
class TestCustomUserModel:
    """Тесты для модели пользователя."""

    def test_create_user(self):
        """Тест создания пользователя."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_superuser(self):
        """Тест создания суперпользователя."""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        assert admin.username == 'admin'
        assert admin.is_active
        assert admin.is_staff
        assert admin.is_superuser

    def test_user_str(self, user):
        """Тест строкового представления пользователя."""
        assert str(user) == user.username

    def test_user_get_absolute_url(self, user):
        """Тест получения URL профиля пользователя."""
        expected_url = reverse('users:profile', kwargs={'username': user.username})
        assert user.get_absolute_url() == expected_url

    def test_user_fields(self, user):
        """Тест дополнительных полей пользователя."""
        user.bio = "Test bio"
        user.contacts = "Test contacts"
        user.save()

        saved_user = User.objects.get(pk=user.pk)
        assert saved_user.bio == "Test bio"
        assert saved_user.contacts == "Test contacts"