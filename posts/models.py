# posts/models.py
from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count
from ckeditor.fields import RichTextField  # Импортируем RichTextField

User = get_user_model()

class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    text = RichTextField(verbose_name="Текст")  # Заменяем TextField на RichTextField
    pub_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата публикации"
    )
    slug = models.SlugField( # Slug был упомянут в задаче S2.2, но не использовался в urls/views
        max_length=200,
        unique=True,
        blank=True, # Разрешим быть пустым, чтобы работала автогенерация
        verbose_name="URL-адрес (slug)"
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_posts',
        blank=True,
        verbose_name="Лайки"
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        blank=True,
        verbose_name="Теги"
    )
    image = models.ImageField(
        upload_to='posts_images/',  # Путь для сохранения изображений
        blank=True,                 # Разрешить пустое значение
        null=True                   # Разрешить NULL в базе данных
    )

    def total_likes(self):
        # """Возвращает общее количество лайков для поста, включая анонимные."""
        # auth_likes = self.likes.count()
        # anon_likes = self.anonymous_likes.count()
        # return auth_likes + anon_likes
        return self.likes.count()

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


    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='disliked_posts',
        blank=True,
        verbose_name="Дизлайки"
    )

    def total_dislikes(self):
        return self.dislikes.count()

class PostImage(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Пост"
    )
    image = models.ImageField(
        upload_to="posts_images/",
        verbose_name="Изображение"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок"
    )

    class Meta:
        verbose_name = "Изображение поста"
        verbose_name_plural = "Изображения постов"
        ordering = ['order']

    def __str__(self):
        return f"Изображение для поста {self.post.title}"

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Пост"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен"
    )
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    level = models.PositiveIntegerField(editable=False)
    def __str__(self):
        return f"Комментарий от {self.author} к посту {self.post.title}"

    def get_absolute_url(self):
        """Возвращает URL для просмотра поста с комментариями."""
        return reverse('posts:post-detail', kwargs={'pk': self.post.pk}) + '#comments'

    def save(self, *args, **kwargs):
        # Автоматически определяем уровень перед сохранением
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0  # Это корневой комментарий
        super().save(*args, **kwargs)

    @property
    def aggregated_reactions(self):
        from django.db.models import Count
        return self.reactions.values('emoji').annotate(count=Count('id')).order_by('-count')

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created_at"]


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="URL-адрес")

    def __str__(self):
        return self.name

    @staticmethod
    def get_popular_tags(limit=5):
        """Возвращает список популярных тегов с количеством постов."""
        return Tag.objects.annotate(
            posts_count=Count('posts')
        ).order_by('-posts_count')[:limit]

    def get_absolute_url(self):
        """Возвращает URL для просмотра постов с данным тегом."""
        return reverse('posts:tag-posts', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['name']

class AnonymousLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='anonymous_likes')
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'session_key')
        verbose_name = "Анонимный лайк"
        verbose_name_plural = "Анонимные лайки"

class CommentReaction(models.Model):
    comment = models.ForeignKey(
        'Comment',
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Используем настройки
        on_delete=models.CASCADE,
        related_name='comment_reactions'
    )
    emoji = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user', 'emoji')