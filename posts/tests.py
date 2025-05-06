from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Post

User = get_user_model()

class PostTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Тестовый пост',
            text='Пример текста',
            author=self.user
        )

    def test_post_list_view(self):
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый пост')

    def test_post_create_auth_required(self):
        # Неавторизованный пользователь
        response = self.client.get(reverse('post_create'))
        self.assertRedirects(response, '/accounts/login/?next=/posts/create/')

        # Авторизованный пользователь
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('post_create'))
        self.assertEqual(response.status_code, 200)

    def test_post_update_permission(self):
        # Попытка редактирования чужого поста
        user2 = User.objects.create_user(username='user2', password='pass123')
        self.client.login(username='user2', password='pass123')
        response = self.client.get(
            reverse('post_update', args=[self.post.slug])
        )
        self.assertEqual(response.status_code, 403)