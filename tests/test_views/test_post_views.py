import pytest
from django.urls import reverse
from posts.models import Post


@pytest.mark.django_db
class TestPostViews:
    """Тесты для представлений постов."""

    def test_post_list_view(self, client, post):
        """Тест списка постов."""
        url = reverse('posts:post-list')
        response = client.get(url)
        assert response.status_code == 200
        assert post.title in response.content.decode()

    def test_post_detail_view(self, client, post):
        """Тест детального просмотра поста."""
        url = reverse('posts:post-detail', kwargs={'pk': post.pk})
        response = client.get(url)
        assert response.status_code == 200
        assert post.title in response.content.decode()
        assert post.text in response.content.decode()

    def test_post_create_view_authenticated(self, authenticated_client):
        """Тест создания поста авторизованным пользователем."""
        url = reverse('posts:post-create')
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_post_create_view_unauthenticated(self, client):
        """Тест создания поста неавторизованным пользователем."""
        url = reverse('posts:post-create')
        response = client.get(url)
        assert response.status_code == 302  # Редирект на страницу входа

    def test_post_create_post(self, authenticated_client, user):
        """Тест отправки формы создания поста."""
        url = reverse('posts:post-create')
        data = {
            'title': 'New Test Post',
            'text': 'This is a new test post content with enough characters',
            'agree_to_rules': True,
            'images-TOTAL_FORMS': '0',
            'images-INITIAL_FORMS': '0',
            'images-MAX_NUM_FORMS': ''
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302  # Редирект после создания

        # Проверяем, что пост создан
        post = Post.objects.get(title='New Test Post')
        assert post.author == user
        assert post.text == 'This is a new test post content with enough characters'

    def test_post_update_view_author(self, authenticated_client, post):
        """Тест редактирования поста автором."""
        url = reverse('posts:post-update', kwargs={'pk': post.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_post_update_view_not_author(self, client, post, another_user):
        """Тест попытки редактирования чужого поста."""
        client.login(username=another_user.username, password='testpass123')
        url = reverse('posts:post-update', kwargs={'pk': post.pk})
        response = client.get(url)
        assert response.status_code == 403  # Запрещено

    def test_post_delete_view_author(self, authenticated_client, post):
        """Тест удаления поста автором."""
        url = reverse('posts:post-delete', kwargs={'pk': post.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200  # Страница подтверждения

        # Подтверждаем удаление
        response = authenticated_client.post(url)
        assert response.status_code == 302  # Редирект после удаления
        assert not Post.objects.filter(pk=post.pk).exists()

    def test_post_like_view(self, authenticated_client, post):
        """Тест лайка поста."""
        url = reverse('posts:post-like', kwargs={'pk': post.pk})
        response = authenticated_client.post(url)
        assert response.status_code == 200

        # Проверяем JSON-ответ
        data = response.json()
        assert data['status'] == 'ok'
        assert data['liked'] == True
        assert data['total_likes'] == 1

    def test_post_comment_view(self, authenticated_client, post):
        """Тест добавления комментария."""
        url = reverse('posts:post-comment', kwargs={'pk': post.pk})
        data = {
            'text': 'This is a test comment'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302  # Редирект после добавления

        # Проверяем, что комментарий создан
        assert post.comments.count() == 1
        comment = post.comments.first()
        assert comment.text == 'This is a test comment'