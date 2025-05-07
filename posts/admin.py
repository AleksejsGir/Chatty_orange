from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Post
from django.utils.html import format_html

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;">', obj.image.url)
        return "-"
    image_preview.short_description = "Превью"
