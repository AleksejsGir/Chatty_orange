# posts/admin.py
from django.contrib import admin
from .models import Post, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'created_at')
    fields = ('author', 'text', 'created_at')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'pub_date', 'comment_count')
    list_filter = ('author', 'pub_date')
    search_fields = ('title', 'text')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CommentInline]

    def comment_count(self, obj):
        return obj.comments.count()

    comment_count.short_description = "Комментарии"

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
