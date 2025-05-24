import pytest
from django.test import Client


@pytest.fixture
def client():
    """Фикстура для тестового клиента."""
    return Client()


@pytest.fixture
def user(db):
    """Фикстура для создания обычного пользователя."""
    # Импортируем модель только когда она нужна
    from django.contrib.auth import get_user_model
    User = get_user_model()

    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123'
    )


@pytest.fixture
def another_user(db):
    """Фикстура для создания второго пользователя."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(client, user):
    """Фикстура для аутентифицированного клиента."""
    client.login(username='testuser', password='testpass123')
    return client


@pytest.fixture
def post(db, user):
    """Фикстура для создания поста."""
    # Импортируем модель только внутри фикстуры
    from posts.models import Post

    return Post.objects.create(
        author=user,
        title='Test Post',
        text='This is a test post content',
        slug='test-post'
    )


@pytest.fixture
def tag(db):
    """Фикстура для создания тега."""
    from posts.models import Tag

    return Tag.objects.create(
        name='TestTag',
        slug='test-tag'
    )


@pytest.fixture
def comment(db, post, user):
    """Фикстура для создания комментария."""
    from posts.models import Comment

    return Comment.objects.create(
        post=post,
        author=user,
        text='This is a test comment'
    )


@pytest.fixture
def subscription(db, user, another_user):
    """Фикстура для создания подписки."""
    from subscriptions.models import Subscription

    return Subscription.objects.create(
        subscriber=user,
        author=another_user
    )


@pytest.fixture
def create_user(db):
    """Фабрика для создания пользователей."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    def make_user(**kwargs):
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        defaults.update(kwargs)
        if 'username' in kwargs:
            defaults['email'] = f"{kwargs['username']}@example.com"
        return User.objects.create_user(**defaults)

    return make_user


@pytest.fixture
def create_post(db):
    """Фабрика для создания постов."""
    from posts.models import Post

    def make_post(**kwargs):
        defaults = {
            'title': 'Test Post',
            'text': 'Test post content'
        }
        defaults.update(kwargs)
        return Post.objects.create(**defaults)

    return make_post

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Автоматически разрешает доступ к БД для всех тестов.
    Это упрощает написание тестов.
    """
    pass


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    """
    Настраивает временное хранилище для медиа-файлов в тестах.
    """
    settings.MEDIA_ROOT = tmpdir.strpath