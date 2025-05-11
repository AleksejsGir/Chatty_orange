# users/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Count, Exists, OuterRef
from .forms import ProfileUpdateForm
from subscriptions.models import Subscription
from posts.models import Post, Comment  # Добавлен импорт Comment

CustomUser = get_user_model()


def home_page_view(request):
    context = {}
    return render(request, 'home.html', context)


def profile_view(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)

    # Добавляем проверку подписки
    is_subscribed = False
    if request.user.is_authenticated and request.user != profile_user:
        is_subscribed = Subscription.objects.filter(
            subscriber=request.user,
            author=profile_user
        ).exists()

    # Получаем несколько последних постов пользователя, с аннотациями
    posts_query = Post.objects.filter(author=profile_user)

    # Добавляем аннотации для подсчета лайков и комментариев
    user_posts = posts_query.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True)
    ).order_by('-pub_date')[:4]

    # Определяем, какие посты лайкнул текущий пользователь
    user_liked_posts = []
    if request.user.is_authenticated:
        # Получаем ID постов, которые лайкнул пользователь
        liked_post_ids = posts_query.filter(likes=request.user).values_list('id', flat=True)
        user_liked_posts = list(liked_post_ids)

    context = {
        'profile_user': profile_user,
        'is_subscribed': is_subscribed,
        'user_posts': user_posts,
        'user_liked_posts': user_liked_posts
    }
    return render(request, 'users/profile.html', context)


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'username': self.request.user.username})

    def test_func(self):
        user = self.get_object()
        return self.request.user == user