# posts/admin.py
# from django.contrib import admin
# from .models import Post, Comment, Tag
#
#
# class CommentInline(admin.TabularInline):
#     model = Comment
#     extra = 0
#     readonly_fields = ('author', 'created_at')
#     fields = ('author', 'text', 'created_at')
#
#
# @admin.register(Tag)
# class TagAdmin(admin.ModelAdmin):
#     list_display = ('name', 'slug', 'post_count')
#     search_fields = ('name', 'slug')
#     prepopulated_fields = {'slug': ('name',)}
#
#     def post_count(self, obj):
#         return obj.posts.count()
#
#     post_count.short_description = "Количество постов"
#
#
# @admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
#     list_display = ('title', 'author', 'pub_date', 'comment_count', 'tag_list')
#     list_filter = ('author', 'pub_date', 'tags')
#     search_fields = ('title', 'text')
#     prepopulated_fields = {'slug': ('title',)}
#     inlines = [CommentInline]
#     filter_horizontal = ('tags',)
#
#     def comment_count(self, obj):
#         return obj.comments.count()
#
#     comment_count.short_description = "Комментарии"
#
#     def tag_list(self, obj):
#         return ", ".join(tag.name for tag in obj.tags.all())
#
#     tag_list.short_description = "Теги"
#
#
# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = ('short_text', 'author', 'post', 'created_at')
#     list_filter = ('author', 'created_at')
#     search_fields = ('text', 'author__username', 'post__title')
#     readonly_fields = ('created_at',)
#     actions = ['approve_comments']
#
#     def short_text(self, obj):
#         return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
#
#     short_text.short_description = "Текст"
#
#     def approve_comments(self, request, queryset):
#         queryset.update(active=True)
#
#     approve_comments.short_description = "Одобрить выбранные комментарии"

from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Comment, Tag


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'created_at')
    fields = ('author', 'text', 'created_at')
    show_change_link = True


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    def post_count(self, obj):
        return obj.posts.count()

    post_count.short_description = "Количество постов"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'pub_date', 'comment_count', 'like_count', 'tag_list', 'has_image')
    list_filter = ('author', 'pub_date', 'tags')
    search_fields = ('title', 'text', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'pub_date'
    inlines = [CommentInline]
    filter_horizontal = ('tags',)

    def comment_count(self, obj):
        return obj.comments.count()

    comment_count.short_description = "Комментарии"

    def like_count(self, obj):
        if hasattr(obj, 'likes'):
            return obj.likes.count()
        return 0

    like_count.short_description = "Лайки"

    def tag_list(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())

    tag_list.short_description = "Теги"

    def has_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "Нет"

    has_image.short_description = "Изображение"

    actions = ['publish_posts', 'unpublish_posts']

    def publish_posts(self, request, queryset):
        queryset.update(is_published=True)  # Предполагается, что есть поле is_published

    publish_posts.short_description = "Опубликовать выбранные посты"

    def unpublish_posts(self, request, queryset):
        queryset.update(is_published=False)  # Предполагается, что есть поле is_published

    unpublish_posts.short_description = "Снять с публикации выбранные посты"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'author', 'post_title', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('text', 'author__username', 'post__title')
    raw_id_fields = ('author', 'post')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    short_text.short_description = "Текст"

    def post_title(self, obj):
        return obj.post.title

    post_title.short_description = "Пост"

    actions = ['approve_comments', 'reject_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_active=True)  # Предполагается, что есть поле is_active

    approve_comments.short_description = "Одобрить выбранные комментарии"

    def reject_comments(self, request, queryset):
        queryset.update(is_active=False)  # Предполагается, что есть поле is_active

    reject_comments.short_description = "Отклонить выбранные комментарии"