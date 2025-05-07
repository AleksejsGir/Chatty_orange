# posts/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse # <<< Убедитесь, что reverse импортирован
from django.utils import timezone

class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    image = models.ImageField(
        upload_to="posts_images/",
        blank=True,
        null=True,
        verbose_name="Изображение"
    )
    pub_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата публикации"
    )
    slug = models.SlugField( # Slug был упомянут в задаче S2.2, но не использовался в urls/views
        max_length=200,
        unique=True,
        blank=True, # Разрешим быть пустым, чтобы автогенерация работала
        verbose_name="URL-адрес (slug)"
    )

    def __str__(self):
        return self.title

    # --- ДОБАВИТЬ ЭТОТ МЕТОД ---
    def get_absolute_url(self):
        """Возвращает URL для просмотра конкретного поста."""
        # Используем имя URL 'post-detail' из posts/urls.py и pk поста
        return reverse('posts:post-detail', kwargs={'pk': self.pk})
    # --- КОНЕЦ МЕТОДА ---

    def save(self, *args, **kwargs):
        if not self.slug: # Генерируем slug только если он пуст
            # Генерируем базовый slug из заголовка
            base_slug = slugify(self.title)
            # Проверяем уникальность и добавляем суффикс при необходимости
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs) # Вызываем родительский метод save

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-pub_date"]