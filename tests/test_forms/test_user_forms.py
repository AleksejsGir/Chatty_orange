import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from users.forms import ProfileUpdateForm
from users.models import CustomUser
from PIL import Image
import io


@pytest.mark.django_db
class TestProfileUpdateForm:
    """Тесты для формы обновления профиля."""

    def test_valid_form(self, user):
        """Тест валидной формы."""
        form_data = {
            'username': 'newusername',
            'email': 'newemail@example.com',
            'bio': 'New bio text',
            'contacts': 'New contacts'
        }
        form = ProfileUpdateForm(data=form_data, instance=user)
        assert form.is_valid()

    def test_duplicate_username(self, user, another_user):
        """Тест на дублирование имени пользователя."""
        form_data = {
            'username': another_user.username,
            'email': user.email
        }
        form = ProfileUpdateForm(data=form_data, instance=user)
        assert not form.is_valid()
        assert 'username' in form.errors
        assert 'Это имя пользователя уже занято' in form.errors['username'][0]

    def test_same_username_allowed(self, user):
        """Тест что пользователь может сохранить свое же имя."""
        form_data = {
            'username': user.username,
            'email': user.email
        }
        form = ProfileUpdateForm(data=form_data, instance=user)
        assert form.is_valid()

    def test_avatar_upload(self, user):
        """Тест загрузки аватара."""
        # Создаем реальное изображение в памяти
        image = Image.new('RGB', (100, 100), color='red')
        image_io = io.BytesIO()
        image.save(image_io, 'JPEG')
        image_io.seek(0)

        # Создаем файл для загрузки
        uploaded_file = SimpleUploadedFile(
            name='test_avatar.jpg',
            content=image_io.read(),
            content_type='image/jpeg'
        )

        form_data = {
            'username': user.username,
            'email': user.email
        }

        # Создаем форму с файлом
        form = ProfileUpdateForm(
            data=form_data,
            files={'avatar': uploaded_file},
            instance=user
        )

        # Проверяем, что форма валидна
        assert form.is_valid(), f"Form errors: {form.errors}"

        # Сохраняем форму и проверяем, что аватар установлен
        updated_user = form.save()
        assert updated_user.avatar is not None
        assert 'test_avatar' in updated_user.avatar.name