import pytest
from django.db import IntegrityError
from subscriptions.models import Subscription


@pytest.mark.django_db
class TestSubscriptionModel:
    """Тесты для модели подписки."""

    def test_create_subscription(self, user, another_user):
        """Тест создания подписки."""
        subscription = Subscription.objects.create(
            subscriber=user,
            author=another_user
        )
        assert subscription.subscriber == user
        assert subscription.author == another_user
        assert subscription.created_at

    def test_subscription_str(self, subscription):
        """Тест строкового представления подписки."""
        expected = f"{subscription.subscriber.username} → {subscription.author.username}"
        assert str(subscription) == expected

    def test_subscription_unique_constraint(self, user, another_user):
        """Тест уникальности подписки."""
        Subscription.objects.create(subscriber=user, author=another_user)

        # Попытка создать дубликат должна вызвать ошибку
        with pytest.raises(IntegrityError):
            Subscription.objects.create(subscriber=user, author=another_user)

    def test_subscription_ordering(self, user):
        """Тест сортировки подписок."""
        from tests.factories import UserFactory
        author1 = UserFactory()
        author2 = UserFactory()

        sub1 = Subscription.objects.create(subscriber=user, author=author1)
        sub2 = Subscription.objects.create(subscriber=user, author=author2)

        subscriptions = Subscription.objects.all()
        # Последняя подписка должна быть первой (ordering = ['-created_at'])
        assert subscriptions[0] == sub2
        assert subscriptions[1] == sub1