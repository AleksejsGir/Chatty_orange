from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone

class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Используем системную настройку
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
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="URL-адрес"
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            while Post.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{self.id or 'copy'}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-pub_date"]