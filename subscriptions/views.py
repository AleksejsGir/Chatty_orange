# Copyright 2024-2025 Aleksejs Giruckis, Igor Pronin, Viktor Yerokhov,
# Maxim Schneider, Ivan Miakinnov, Eugen Maljas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# subscriptions/views.py

from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Count, Exists, OuterRef
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
import logging

from posts.models import Post
from .models import Subscription

User = get_user_model()
logger = logging.getLogger(__name__)


@method_decorator(ensure_csrf_cookie, name='dispatch')  # ✅ CSRF защита
class SubscriptionToggleView(LoginRequiredMixin, View):
    """
    Представление для подписки/отписки от пользователя.
    Поддерживает AJAX и обычные запросы с полной CSRF защитой.
    """

    def post(self, request, username):
        try:
            # Получаем автора, на которого подписываемся или от которого отписываемся
            author = get_object_or_404(User, username=username)

            # ✅ Логируем запрос для мониторинга
            logger.info(f"Subscription toggle: {request.user.username} -> {username}")

            # Проверяем, не пытается ли пользователь подписаться на самого себя
            if request.user == author:
                error_msg = 'Вы не можете подписаться на самого себя'

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': error_msg
                    }, status=400)
                else:
                    return redirect('users:profile', username=username)

            # Проверяем, подписан ли уже пользователь
            subscription = Subscription.objects.filter(
                subscriber=request.user,
                author=author
            ).first()

            if subscription:
                # Если подписка существует, удаляем её (отписываемся)
                subscription.delete()
                is_subscribed = False
                message = f'Вы отписались от @{author.username}'
                logger.info(f"Unsubscribed: {request.user.username} from {username}")
            else:
                # Если подписки нет, создаём её (подписываемся)
                try:
                    Subscription.objects.create(subscriber=request.user, author=author)
                    is_subscribed = True
                    message = f'Вы подписались на @{author.username}'
                    logger.info(f"Subscribed: {request.user.username} to {username}")
                except IntegrityError:
                    # Обработка редкого случая одновременного создания подписки
                    error_msg = 'Подписка уже существует'
                    logger.warning(f"IntegrityError during subscription: {request.user.username} -> {username}")

                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'error',
                            'message': error_msg
                        }, status=400)
                    else:
                        return redirect('users:profile', username=username)

            # Получаем URL для перенаправления после завершения операции
            next_url = request.POST.get('next')

            # Возвращаем ответ в зависимости от типа запроса (AJAX или обычный)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # ✅ ИСПРАВЛЕННЫЙ JSON-ответ для совместимости с JavaScript
                subscribers_count = author.subscribers.count()

                return JsonResponse({
                    'status': 'success',
                    'subscribed': is_subscribed,  # ✅ ИЗМЕНЕНО: 'subscribed' вместо 'is_subscribed'
                    'message': message,
                    'subscribers_count': subscribers_count,
                    'username': username  # ✅ ДОБАВЛЕНО: для дополнительной проверки в JS
                })
            else:
                # Для обычного запроса перенаправляем на URL из параметра next или на профиль
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('users:profile', username=username)

        except Exception as e:
            # ✅ УЛУЧШЕННАЯ обработка ошибок
            logger.error(f"Subscription toggle error for {request.user.username} -> {username}: {e}")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Произошла ошибка при обработке запроса'
                }, status=500)
            else:
                return redirect('users:profile', username=username)


class FollowersListView(ListView):
    """
    Отображает список подписчиков пользователя.
    """
    model = Subscription
    template_name = 'subscriptions/followers.html'
    context_object_name = 'subscriptions'
    paginate_by = 10

    def get_queryset(self):
        self.profile_user = get_object_or_404(User, username=self.kwargs['username'])
        # Получаем подписки, где profile_user является автором (т.е. его подписчики)
        return Subscription.objects.filter(author=self.profile_user).select_related('subscriber')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user

        # Если пользователь авторизован, определяем, на кого из списка он подписан
        if self.request.user.is_authenticated:
            subscribed_to = set(
                Subscription.objects.filter(
                    subscriber=self.request.user,
                    author__in=[sub.subscriber for sub in context['subscriptions']]
                ).values_list('author_id', flat=True)
            )
            context['subscribed_to'] = subscribed_to

        return context


class FollowingListView(ListView):
    """
    Отображает список подписок пользователя (на кого он подписан).
    """
    model = Subscription
    template_name = 'subscriptions/following.html'
    context_object_name = 'subscriptions'
    paginate_by = 10

    def get_queryset(self):
        self.profile_user = get_object_or_404(User, username=self.kwargs['username'])
        # Получаем подписки, где profile_user является подписчиком
        return Subscription.objects.filter(subscriber=self.profile_user).select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        return context


class FeedView(LoginRequiredMixin, ListView):
    """
    Отображает ленту постов от пользователей, на которых подписан текущий пользователь.
    """
    model = Post
    template_name = 'subscriptions/feed.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Post.objects.none()

        # Получаем ID пользователей, на которых подписан текущий пользователь
        following_users = Subscription.objects.filter(
            subscriber=self.request.user
        ).values_list('author_id', flat=True)

        # Возвращаем посты от этих пользователей с аннотациями и предзагрузкой связанных данных
        return Post.objects.filter(
            author_id__in=following_users
        ).select_related(
            'author'  # Загружаем информацию об авторе одним запросом
        ).prefetch_related(
            'images',  # ВАЖНО! Загружаем все изображения для постов
            'likes',  # Загружаем лайки для проверки, лайкнул ли текущий пользователь
            'tags',  # Загружаем теги, если они отображаются в ленте
            'comments'  # Загружаем комментарии для подсчета
        ).annotate(
            num_comments=Count('comments', distinct=True),
            num_likes=Count('likes', distinct=True)
        ).order_by('-pub_date')