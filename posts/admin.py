# posts/admin.py
from django.contrib import admin
from .models import Post, Comment, Tag


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'created_at')
    fields = ('author', 'text', 'created_at')


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
    list_display = ('title', 'author', 'pub_date', 'comment_count', 'tag_list')
    list_filter = ('author', 'pub_date', 'tags')
    search_fields = ('title', 'text')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CommentInline]
    filter_horizontal = ('tags',)

    def comment_count(self, obj):
        return obj.comments.count()

    comment_count.short_description = "Комментарии"

    def tag_list(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())

    tag_list.short_description = "Теги"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'author', 'post', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('text', 'author__username', 'post__title')
    readonly_fields = ('created_at',)
    actions = ['approve_comments']

    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    short_text.short_description = "Текст"

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

    approve_comments.short_description = "Одобрить выбранные комментарии"