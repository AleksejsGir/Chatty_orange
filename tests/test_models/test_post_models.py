import pytest
from django.urls import reverse
from posts.models import Post, Comment, Tag
from tests.factories import PostFactory, UserFactory, TagFactory


@pytest.mark.django_db
class TestPostModel:
    """Тесты для модели поста."""

    def test_create_post(self, user):
        """Тест создания поста."""
        post = Post.objects.create(
            author=user,
            title='Test Post',
            text='Test content'
        )
        assert post.title == 'Test Post'
        assert post.text == 'Test content'
        assert post.author == user
        assert post.slug  # Slug должен генерироваться автоматически

    def test_post_str(self, post):
        """Тест строкового представления поста."""
        assert str(post) == post.title

    def test_post_get_absolute_url(self, post):
        """Тест получения URL поста."""
        expected_url = reverse('posts:post-detail', kwargs={'pk': post.pk})
        assert post.get_absolute_url() == expected_url

    def test_post_slug_generation(self, user):
        """Тест автоматической генерации slug."""
        post = Post.objects.create(
            author=user,
            title='Test Post Title'
        )
        assert post.slug == 'test-post-title'

    def test_post_slug_uniqueness(self, user):
        """Тест уникальности slug."""
        post1 = Post.objects.create(
            author=user,
            title='Same Title'
        )
        post2 = Post.objects.create(
            author=user,
            title='Same Title'
        )
        assert post1.slug != post2.slug
        assert post2.slug == 'same-title-1'

    def test_post_likes(self, post, user, another_user):
        """Тест функционала лайков."""
        assert post.total_likes() == 0

        post.likes.add(user)
        assert post.total_likes() == 1

        post.likes.add(another_user)
        assert post.total_likes() == 2

        post.likes.remove(user)
        assert post.total_likes() == 1

    def test_post_tags(self, post, tag):
        """Тест работы с тегами."""
        post.tags.add(tag)
        assert tag in post.tags.all()
        assert post in tag.posts.all()


@pytest.mark.django_db
class TestCommentModel:
    """Тесты для модели комментария."""

    def test_create_comment(self, post, user):
        """Тест создания комментария."""
        comment = Comment.objects.create(
            post=post,
            author=user,
            text='Test comment'
        )
        assert comment.post == post
        assert comment.author == user
        assert comment.text == 'Test comment'
        assert comment.is_active

    def test_comment_str(self, comment):
        """Тест строкового представления комментария."""
        expected = f"Комментарий от {comment.author} к посту {comment.post.title}"
        assert str(comment) == expected

    def test_comment_ordering(self, post, user):
        """Тест сортировки комментариев."""
        comment1 = Comment.objects.create(post=post, author=user, text='First')
        comment2 = Comment.objects.create(post=post, author=user, text='Second')

        comments = Comment.objects.all()
        # Последний комментарий должен быть первым (ordering = ['-created_at'])
        assert comments[0] == comment2
        assert comments[1] == comment1


@pytest.mark.django_db
class TestTagModel:
    """Тесты для модели тега."""

    def test_create_tag(self):
        """Тест создания тега."""
        tag = Tag.objects.create(
            name='TestTag',
            slug='test-tag'
        )
        assert tag.name == 'TestTag'
        assert tag.slug == 'test-tag'

    def test_tag_str(self, tag):
        """Тест строкового представления тега."""
        assert str(tag) == tag.name

    def test_tag_get_absolute_url(self, tag):
        """Тест получения URL тега."""
        expected_url = reverse('posts:tag-posts', kwargs={'slug': tag.slug})
        assert tag.get_absolute_url() == expected_url

    def test_popular_tags(self):
        """Тест получения популярных тегов."""
        # Создаем теги и посты
        user = UserFactory()
        tags = [TagFactory() for _ in range(10)]

        # Создаем посты с разным количеством для каждого тега
        for i, tag in enumerate(tags[:5]):
            for _ in range(5 - i):
                post = PostFactory(author=user)
                post.tags.add(tag)

        popular = Tag.get_popular_tags(limit=3)
        assert len(popular) == 3
        # Проверяем, что теги отсортированы по популярности
        assert popular[0].posts_count >= popular[1].posts_count
        assert popular[1].posts_count >= popular[2].posts_count