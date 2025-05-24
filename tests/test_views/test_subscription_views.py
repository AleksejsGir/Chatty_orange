import pytest
from django.urls import reverse
from subscriptions.models import Subscription


@pytest.mark.django_db
class TestSubscriptionViews:
    """Тесты для представлений подписок."""

    def test_subscription_toggle_subscribe(self, authenticated_client, user, another_user):
        """Тест подписки на пользователя."""
        url = reverse('subscriptions:toggle', kwargs={'username': another_user.username})
        response = authenticated_client.post(url)
        assert response.status_code == 302  # Редирект

        # Проверяем, что подписка создана
        assert Subscription.objects.filter(
            subscriber=user,
            author=another_user
        ).exists()

    def test_subscription_toggle_unsubscribe(self, authenticated_client, user, another_user):
        """Тест отписки от пользователя."""
        # Сначала создаем подписку
        Subscription.objects.create(subscriber=user, author=another_user)

        url = reverse('subscriptions:toggle', kwargs={'username': another_user.username})
        response = authenticated_client.post(url)
        assert response.status_code == 302  # Редирект

        # Проверяем, что подписка удалена
        assert not Subscription.objects.filter(
            subscriber=user,
            author=another_user
        ).exists()

    def test_subscription_toggle_self(self, authenticated_client, user):
        """Тест попытки подписаться на самого себя."""
        url = reverse('subscriptions:toggle', kwargs={'username': user.username})
        response = authenticated_client.post(url)
        assert response.status_code == 302  # Редирект

        # Проверяем, что подписка не создана
        assert not Subscription.objects.filter(
            subscriber=user,
            author=user
        ).exists()

    def test_followers_list_view(self, client, user):
        """Тест списка подписчиков."""
        url = reverse('subscriptions:followers', kwargs={'username': user.username})
        response = client.get(url)
        assert response.status_code == 200

    def test_following_list_view(self, client, user):
        """Тест списка подписок."""
        url = reverse('subscriptions:following', kwargs={'username': user.username})
        response = client.get(url)
        assert response.status_code == 200

    def test_feed_view_authenticated(self, authenticated_client, user, another_user, post):
        """Тест ленты подписок для авторизованного пользователя."""
        # Создаем подписку
        Subscription.objects.create(subscriber=user, author=post.author)

        url = reverse('subscriptions:feed')
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert post.title in response.content.decode()

    def test_feed_view_unauthenticated(self, client):
        """Тест ленты подписок для неавторизованного пользователя."""
        url = reverse('subscriptions:feed')
        response = client.get(url)
        assert response.status_code == 302  # Редирект на страницу входа