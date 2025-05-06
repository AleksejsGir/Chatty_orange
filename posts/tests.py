from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
# from .models import Post # Раскомментировать, когда модель Post будет готова
# from .forms import PostForm # Раскомментировать, когда форма PostForm будет готова

# CustomUser = get_user_model()

class PostViewsTests(TestCase):
    """
    Тесты для представлений приложения posts.
    """
    @classmethod
    def setUpTestData(cls):
        # TODO: Создать тестовых пользователей (автор, другой пользователь, аноним)
        # cls.user_author = CustomUser.objects.create_user(username='author_user', password='password123')
        # cls.another_user = CustomUser.objects.create_user(username='another_user', password='password123')
        # cls.guest_client = Client()
        # cls.author_client = Client()
        # cls.author_client.login(username='author_user', password='password123')
        # cls.another_client = Client()
        # cls.another_client.login(username='another_user', password='password123')

        # TODO: Создать несколько тестовых постов
        # cls.post1 = Post.objects.create(author=cls.user_author, title='Тестовый пост 1', text='Текст поста 1', slug='test-post-1')
        # cls.post2 = Post.objects.create(author=cls.user_author, title='Тестовый пост 2', text='Текст поста 2', slug='test-post-2')
        pass

    def test_post_list_view_status_code(self):
        # TODO: Проверить, что страница списка постов (posts:list) возвращает статус 200
        # response = self.client.get(reverse('posts:list'))
        # self.assertEqual(response.status_code, 200)
        pass

    def test_post_detail_view_status_code(self):
        # TODO: Проверить, что страница детального просмотра поста (posts:detail) возвращает статус 200 для существующего поста
        # response = self.client.get(reverse('posts:detail', kwargs={'slug': self.post1.slug}))
        # self.assertEqual(response.status_code, 200)
        pass

    def test_post_create_view_get_for_authenticated_user(self):
        # TODO: Проверить, что страница создания поста (posts:create) возвращает статус 200 для авторизованного пользователя
        # response = self.author_client.get(reverse('posts:create'))
        # self.assertEqual(response.status_code, 200)
        pass

    def test_post_create_view_redirect_for_anonymous_user(self):
        # TODO: Проверить, что неавторизованный пользователь перенаправляется со страницы создания поста на страницу логина
        # response = self.guest_client.get(reverse('posts:create'))
        # self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, f"{reverse('account_login')}?next={reverse('posts:create')}")
        pass

class PostFormTests(TestCase):
    """
    Тесты для форм приложения posts.
    """
    # TODO: Написать тесты для PostForm (валидация, сохранение)
    pass

class PostModelTests(TestCase):
    """
    Тесты для моделей приложения posts.
    """
    # TODO: Написать тесты для модели Post (__str__, get_absolute_url, генерация slug)
    pass

# <!-- TODO: Добавить тесты для редактирования и удаления постов, проверяя права доступа. -->
# <!-- TODO: Добавить тесты для пагинации на странице списка постов. -->
# <!-- TODO: Рассмотреть использование фикстур или factory_boy для создания тестовых данных. -->