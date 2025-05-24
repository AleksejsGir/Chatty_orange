import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.models import Post, Comment
from subscriptions.models import Subscription
from django.test import override_settings

User = get_user_model()


@pytest.mark.django_db
class TestUserFlows:
    """Интеграционные тесты пользовательских сценариев."""

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION='none',  # Отключаем верификацию email для теста
        ACCOUNT_EMAIL_REQUIRED=False
    )
    def test_user_registration_and_post_creation_flow(self, client):
        """Тест полного сценария: регистрация → создание поста → комментарий."""
        # 1. Регистрация пользователя
        signup_url = reverse('account_signup')
        signup_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }

        # Отправляем форму регистрации
        response = client.post(signup_url, signup_data, follow=True)

        # Проверяем, что пользователь создан
        assert User.objects.filter(username='newuser').exists()
        user = User.objects.get(username='newuser')

        # 2. Принудительно логинимся (обходим подтверждение email)
        client.force_login(user)

        # 3. Создание поста
        create_post_url = reverse('posts:post-create')
        post_data = {
            'title': 'My First Post',
            'text': 'This is my first post on Chatty platform! It has enough characters now.',
            'agree_to_rules': True,
            'images-TOTAL_FORMS': '0',
            'images-INITIAL_FORMS': '0',
            'images-MAX_NUM_FORMS': ''
        }
        response = client.post(create_post_url, post_data)

        # Проверяем редирект после создания
        assert response.status_code == 302

        # Проверяем, что пост создан
        assert Post.objects.filter(title='My First Post').exists()
        post = Post.objects.get(title='My First Post')
        assert post.author == user

        # 4. Добавление комментария к посту
        comment_url = reverse('posts:post-comment', kwargs={'pk': post.pk})
        comment_data = {
            'text': 'This is my first comment!'
        }
        response = client.post(comment_url, comment_data)
        assert response.status_code == 302

        # Проверяем, что комментарий создан
        assert Comment.objects.filter(post=post).exists()
        comment = Comment.objects.get(post=post)
        assert comment.text == 'This is my first comment!'
        assert comment.author == user

    def test_subscription_and_feed_flow(self, client):
        """Тест сценария: подписка на пользователя → просмотр ленты."""
        # Создаем пользователей
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )

        # Создаем посты для user2
        post1 = Post.objects.create(
            author=user2,
            title='Post from User2',
            text='This is a post from user2 with enough content'
        )

        # 1. Входим как user1
        client.login(username='user1', password='pass123')

        # 2. Подписываемся на user2
        subscribe_url = reverse('subscriptions:toggle', kwargs={'username': 'user2'})
        response = client.post(subscribe_url)
        assert response.status_code == 302

        # Проверяем подписку
        assert Subscription.objects.filter(
            subscriber=user1,
            author=user2
        ).exists()

        # 3. Проверяем ленту подписок
        feed_url = reverse('subscriptions:feed')
        response = client.get(feed_url)
        assert response.status_code == 200
        assert 'Post from User2' in response.content.decode()

    def test_like_and_comment_interaction_flow(self, client, user, another_user):
        """Тест взаимодействия: лайки и комментарии."""
        # Создаем пост
        post = Post.objects.create(
            author=user,
            title='Popular Post',
            text='This post will get likes and comments with enough content'
        )

        # 1. Входим как another_user
        client.login(username=another_user.username, password='testpass123')

        # 2. Лайкаем пост
        like_url = reverse('posts:post-like', kwargs={'pk': post.pk})
        response = client.post(like_url)
        assert response.status_code == 200
        data = response.json()
        assert data['liked'] == True
        assert data['total_likes'] == 1

        # 3. Комментируем пост
        comment_url = reverse('posts:post-comment', kwargs={'pk': post.pk})
        comment_data = {'text': 'Great post!'}
        response = client.post(comment_url, comment_data)
        assert response.status_code == 302

        # 4. Проверяем детальную страницу поста
        detail_url = reverse('posts:post-detail', kwargs={'pk': post.pk})
        response = client.get(detail_url)
        assert response.status_code == 200
        assert 'Great post!' in response.content.decode()

    def test_profile_update_flow(self, authenticated_client, user):
        """Тест обновления профиля пользователя."""
        # 1. Переходим на страницу редактирования профиля
        edit_url = reverse('users:profile-edit', kwargs={'pk': user.pk})
        response = authenticated_client.get(edit_url)
        assert response.status_code == 200

        # 2. Обновляем профиль
        update_data = {
            'username': user.username,
            'email': 'updated@example.com',
            'bio': 'I am a Chatty user!',
            'contacts': 'Twitter: @chattyuser'
        }
        response = authenticated_client.post(edit_url, update_data)
        assert response.status_code == 302

        # 3. Проверяем обновленный профиль
        profile_url = reverse('users:profile', kwargs={'username': user.username})
        response = authenticated_client.get(profile_url)
        assert response.status_code == 200
        assert 'I am a Chatty user!' in response.content.decode()
        assert 'Twitter: @chattyuser' in response.content.decode()
        assert 'updated@example.com' in response.content.decode()