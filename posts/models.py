from django.db import models

# Create your models here.
# posts/models.py


from django.db import models
from django.conf import settings

class Post(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title




#
# from django.conf import settings
#
# from django.db import models
# from django.contrib.auth.models import User
#
# class Post(models.Model):
#     title = models.CharField(max_length=200)
#     text = models.TextField()
#     image = models.ImageField(upload_to='post_images/', null=True, blank=True)
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.title
#
#
# class Post(models.Model):
#     author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
