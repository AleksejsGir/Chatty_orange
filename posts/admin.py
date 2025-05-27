from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Comment, Tag, PostImage # Добавлен PostImage

# Используем CKEditor виджет для поля text в админке
from django.db import models
from ckeditor.widgets import CKEditorWidget


class CommentInline(admin.TabularInline): # или admin.StackedInline для другого вида
    model = Comment
    extra = 0 # Не показывать пустые формы по умолчанию
    readonly_fields = ('author', 'text_preview', 'created_at', 'is_active') # Добавил is_active
    fields = ('author', 'text_preview', 'created_at', 'is_active')
    can_delete = True # Разрешить удаление комментариев отсюда
    show_change_link = True # Ссылка на редактирование комментария

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = "Текст комментария"


class PostImageInline(admin.TabularInline): # или admin.StackedInline
    model = PostImage
    extra = 1 # Показать одну пустую форму для добавления изображения
    fields = ('image', 'order')
    # Можно добавить readonly_fields, если нужно (например, для отображения превью)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count_display') # Переименовал для ясности
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    def post_count_display(self, obj):
        return obj.posts.count()
    post_count_display.short_description = "Кол-во постов"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'pub_date',
        'display_first_image_thumbnail',
        'comment_count_display',
        'like_count_display',
        'dislike_count_display',
        'tag_list_display'
    )
    list_filter = ('author', 'pub_date', 'tags')
    search_fields = ('title', 'text', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',) # Удобно для выбора автора, если их много
    date_hierarchy = 'pub_date'
    filter_horizontal = ('tags', 'likes', 'dislikes') # Добавил likes и dislikes для удобного управления
    inlines = [PostImageInline, CommentInline] # Добавлен PostImageInline

    # Используем CKEditor для поля text
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()}, # Если text был TextField
        # Если text уже RichTextField, Django сам подхватит виджет CKEditor.
        # Но если вы хотите переопределить конфигурацию CKEditor для админки:
        # 'text': {'widget': CKEditorWidget(config_name='awesome_ckeditor')} # (config_name из settings.CKEDITOR_CONFIGS)
    }
    # Если Post.text - это RichTextField, то следующая строка не обязательна,
    # но если это models.TextField, то она нужна.
    # Так как в вашей модели Post.text это RichTextField, эта секция formfield_overrides
    # для поля 'text' может быть не нужна, CKEditor должен примениться автоматически.
    # Оставим ее как пример, если бы Post.text был обычным TextField.

    def display_first_image_thumbnail(self, obj):
        first_image_obj = obj.images.order_by('order').first() # Берем первое по порядку
        if first_image_obj and first_image_obj.image:
            return format_html('<img src="{}" width="70" height="50" style="object-fit: cover;" />', first_image_obj.image.url)
        return "Нет изображения"
    display_first_image_thumbnail.short_description = "Превью"

    def comment_count_display(self, obj):
        return obj.comments.count()
    comment_count_display.short_description = "Коммент."

    def like_count_display(self, obj):
        return obj.likes.count()
    like_count_display.short_description = "Лайки"

    def dislike_count_display(self, obj):
        return obj.dislikes.count()
    dislike_count_display.short_description = "Дизлайки"

    def tag_list_display(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all()[:3]) + ('...' if obj.tags.count() > 3 else '')
    tag_list_display.short_description = "Теги"

    # Пример actions, если у вас есть поле is_published в модели Post
    # actions = ['publish_selected', 'unpublish_selected']
    #
    # def publish_selected(self, request, queryset):
    #     queryset.update(is_published=True)
    # publish_selected.short_description = "Опубликовать выбранные посты"
    #
    # def unpublish_selected(self, request, queryset):
    #     queryset.update(is_published=False)
    # unpublish_selected.short_description = "Снять с публикации выбранные посты"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'short_text_display', 'post_link', 'created_at', 'is_active')
    list_filter = ('author', 'created_at', 'is_active', 'post')
    search_fields = ('text', 'author__username', 'post__title')
    raw_id_fields = ('author', 'post')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    list_editable = ('is_active',) # Позволяет менять is_active прямо из списка
    actions = ['mark_as_active', 'mark_as_inactive']

    # Переопределяем поле text, чтобы использовать CKEditor (если Comment.text - TextField)
    # Если Comment.text - это RichTextField, то это не обязательно.
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},
    }

    def short_text_display(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text_display.short_description = "Текст комментария"

    def post_link(self, obj):
        # Ссылка на пост в админке
        url = reverse('admin:posts_post_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, obj.post.title)
    post_link.short_description = "Пост"
    post_link.admin_order_field = 'post' # Разрешаем сортировку по этому полю

    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)
    mark_as_active.short_description = "Одобрить выбранные комментарии"

    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
    mark_as_inactive.short_description = "Отклонить выбранные комментарии"

# Не забываем зарегистрировать PostImage, если хотим управлять ими отдельно
@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('post_title', 'image_thumbnail', 'order')
    list_filter = ('post',)
    search_fields = ('post__title',)
    raw_id_fields = ('post',)
    list_editable = ('order',)

    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = "Заголовок поста"
    post_title.admin_order_field = 'post__title'

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="70" height="50" style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"
    image_thumbnail.short_description = "Изображение"

# <!-- TODO: Проверить, что CKEditor корректно работает для полей Post.text и Comment.text в админке. -->
# <!-- TODO: Если поле is_published не существует в модели Post, удалить связанные actions или добавить поле. -->
# <!-- TODO: Настроить виджеты для ManyToMany полей (likes, dislikes) в PostAdmin, если filter_horizontal не устраивает. -->