import pytest
from posts.forms import PostForm, CommentForm
from posts.models import Tag


@pytest.mark.django_db
class TestPostForm:
    """Тесты для формы создания поста."""

    def test_valid_form(self, user):
        """Тест валидной формы поста."""
        form_data = {
            'title': 'Test Post Title',
            'text': 'This is a test post content with more than 10 characters',
            'agree_to_rules': True
        }
        form = PostForm(data=form_data, user=user)
        assert form.is_valid()

    def test_title_too_short(self, user):
        """Тест слишком короткого заголовка."""
        form_data = {
            'title': 'Test',  # Меньше 5 символов
            'text': 'This is a test post content',
            'agree_to_rules': True
        }
        form = PostForm(data=form_data, user=user)
        assert not form.is_valid()
        assert 'title' in form.errors
        assert 'Заголовок должен содержать минимум 5 символов' in form.errors['title'][0]

    def test_text_too_short(self, user):
        """Тест слишком короткого текста."""
        form_data = {
            'title': 'Test Post Title',
            'text': 'Short',  # Меньше 10 символов
            'agree_to_rules': True
        }
        form = PostForm(data=form_data, user=user)
        assert not form.is_valid()
        assert 'text' in form.errors
        assert 'Текст поста должен содержать минимум 10 символов' in form.errors['text'][0]

    def test_agree_to_rules_required(self, user):
        """Тест обязательности согласия с правилами."""
        form_data = {
            'title': 'Test Post Title',
            'text': 'This is a test post content',
            'agree_to_rules': False
        }
        form = PostForm(data=form_data, user=user)
        assert not form.is_valid()
        assert 'agree_to_rules' in form.errors

    def test_forbidden_tags(self, user):
        """Тест запрещенных тегов."""
        # Создаем запрещенный тег
        forbidden_tag = Tag.objects.create(name='политика', slug='politics')

        form_data = {
            'title': 'Test Post Title',
            'text': 'This is a test post content',
            'tags': [forbidden_tag.id],
            'agree_to_rules': True
        }
        form = PostForm(data=form_data, user=user)
        assert not form.is_valid()
        assert 'tags' in form.errors


@pytest.mark.django_db
class TestCommentForm:
    """Тесты для формы комментария."""

    def test_valid_form(self):
        """Тест валидной формы комментария."""
        form_data = {
            'text': 'This is a test comment'
        }
        form = CommentForm(data=form_data)
        assert form.is_valid()

    def test_text_too_short(self):
        """Тест слишком короткого комментария."""
        form_data = {
            'text': 'Hi'  # Меньше 3 символов
        }
        form = CommentForm(data=form_data)
        assert not form.is_valid()
        assert 'text' in form.errors
        assert 'Комментарий должен содержать минимум 3 символа' in form.errors['text'][0]