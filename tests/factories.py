import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from posts.models import Post, Comment, Tag
from subscriptions.models import Subscription

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Фабрика для создания пользователей."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    bio = factory.Faker('text', max_nb_chars=200)


class PostFactory(DjangoModelFactory):
    """Фабрика для создания постов."""

    class Meta:
        model = Post

    author = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f'Test Post {n}')
    text = factory.Faker('text')
    slug = factory.Sequence(lambda n: f'test-post-{n}')


class CommentFactory(DjangoModelFactory):
    """Фабрика для создания комментариев."""

    class Meta:
        model = Comment

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    text = factory.Faker('text', max_nb_chars=200)


class TagFactory(DjangoModelFactory):
    """Фабрика для создания тегов."""

    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f'tag{n}')
    slug = factory.Sequence(lambda n: f'tag-{n}')