# Generated by Django 5.1.5 on 2025-05-15 18:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_post_dislikes'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnonymousLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=40)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='anonymous_likes', to='posts.post')),
            ],
            options={
                'verbose_name': 'Анонимный лайк',
                'verbose_name_plural': 'Анонимные лайки',
                'unique_together': {('post', 'session_key')},
            },
        ),
    ]
