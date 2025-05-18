# posts/views.py
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Count, Q
from django.views.generic.detail import SingleObjectMixin
from django.views import View

from .models import Post, Comment, Tag
from .forms import PostForm, CommentForm
from subscriptions.models import Subscription  # Добавляем импорт модели подписок

from django.shortcuts import render

User = get_user_model()  # Получаем модель пользователя


class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Аннотируем количеством комментариев и лайков
        user = self.request.user
        if user.is_staff:
            queryset = queryset.annotate(
                num_comments=Count('comments', distinct=True),
                num_likes=Count('likes', distinct=True),
                num_dislikes = Count('dislikes', distinct=True)
            )
        else:
            queryset = queryset.annotate(
                num_comments=Count('comments',filter=Q(comments__is_active=True), distinct=True),
                num_likes=Count('likes', distinct=True),
                num_dislikes = Count('dislikes', distinct=True)
            )

        # Предзагружаем автора для эффективности
        queryset = queryset.select_related('author')

        # Определяем тип фильтрации
        filter_type = self.request.GET.get('filter', 'latest')

        if filter_type == 'popular':
            # Популярные посты - сортировка по количеству лайков
            queryset = queryset.order_by('-num_likes', '-pub_date')
        elif filter_type == 'subscriptions' and self.request.user.is_authenticated:
            # Посты от подписок - только от авторов, на которых подписан пользователь
            try:
                subscribed_to = Subscription.objects.filter(
                    subscriber=self.request.user
                ).values_list('author_id', flat=True)

                queryset = queryset.filter(author_id__in=subscribed_to).order_by('-pub_date')
            except Exception as e:
                # В случае ошибки - показываем обычную ленту
                print(f"Error filtering by subscriptions: {e}")
                queryset = queryset.order_by('-pub_date')
        else:
            # По умолчанию - последние посты
            queryset = queryset.order_by('-pub_date')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Добавляем текущий фильтр в контекст
        context['current_filter'] = self.request.GET.get('filter', 'latest')

        # Добавляем популярные теги
        context['popular_tags'] = Tag.get_popular_tags()

        if self.request.user.is_authenticated:
            try:
                # Получаем ID пользователей, на которых подписан текущий пользователь
                subscribed_to = Subscription.objects.filter(
                    subscriber=self.request.user
                ).values_list('author_id', flat=True)

                # Получаем рекомендуемых пользователей (не включая тех, на кого уже подписан, и себя)
                context['suggested_users'] = User.objects.exclude(
                    id__in=list(subscribed_to) + [self.request.user.id]
                ).annotate(
                    subscribers_count=Count('subscribers')
                ).order_by('-subscribers_count')[:3]  # Показываем 3 самых популярных пользователя
            except Exception as e:
                # В случае ошибки просто не добавляем рекомендации
                context['suggested_users'] = []
                print(f"Error getting suggested users: {e}")

        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'
    paginate_comments_by = 10  # Количество комментариев на странице

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()

        user = self.request.user
        if user.is_staff:
            comments_qs = self.object.comments.all().order_by('-created_at')
        else:
            comments_qs = self.object.comments.filter(is_active=True).order_by('-created_at')

        # Пагинация комментариев
        paginator = Paginator(comments_qs, self.paginate_comments_by)
        page_number = self.request.GET.get('comment_page')
        context['comments'] = paginator.get_page(page_number)

        # Добавляем популярные теги
        context['popular_tags'] = Tag.get_popular_tags()

        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('posts:post-list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostCommentView(LoginRequiredMixin, SingleObjectMixin, View):
    model = Post
    form_class = CommentForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            return redirect(self.object.get_absolute_url() + '#comments')

        # Если форма невалидна, вернемся к детальному просмотру с ошибками
        return self.render_to_response(
            self.get_context_data(
                post=self.object,
                comment_form=form
            )
        )


class PostDetailWithComments(View):
    def get(self, request, *args, **kwargs):
        view = PostDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = PostCommentView.as_view()
        return view(request, *args, **kwargs)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'posts/comment_confirm_delete.html'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author or self.request.user.is_staff

    def get_success_url(self):
        return self.object.post.get_absolute_url() + '#comments'


# posts/views.py (PostLikeView)
@method_decorator(csrf_exempt, name='dispatch')
class PostLikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs.get('pk'))
        user = request.user

        with transaction.atomic():
            # Удаляем дизлайк если есть
            if post.dislikes.filter(id=user.id).exists():
                post.dislikes.remove(user)
                removed_dislike = True
            else:
                removed_dislike = False

            # Обрабатываем лайк
            if post.likes.filter(id=user.id).exists():
                post.likes.remove(user)
                liked = False
            else:
                post.likes.add(user)
                liked = True

        return JsonResponse({
            'status': 'ok',
            'liked': liked,
            'removed_dislike': removed_dislike,
            'total_likes': post.likes.count(),
            'total_dislikes': post.dislikes.count()
        })


# posts/views.py (PostDislikeView)
@method_decorator(csrf_exempt, name='dispatch')
class PostDislikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs.get('pk'))
        user = request.user

        with transaction.atomic():
            # Удаляем лайк если есть
            if post.likes.filter(id=user.id).exists():
                post.likes.remove(user)
                removed_like = True
            else:
                removed_like = False

            # Обрабатываем дизлайк
            if post.dislikes.filter(id=user.id).exists():
                post.dislikes.remove(user)
                disliked = False
            else:
                post.dislikes.add(user)
                disliked = True

        return JsonResponse({
            'status': 'ok',
            'disliked': disliked,
            'removed_like': removed_like,
            'total_dislikes': post.dislikes.count(),
            'total_likes': post.likes.count()
        })

class TagPostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        queryset = Post.objects.filter(tags=self.tag).annotate(
            num_comments=Count('comments', distinct=True),
            num_likes=Count('likes', distinct=True)
        ).select_related('author').order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filter'] = 'tag'
        context['current_tag'] = self.tag
        context['page_title'] = f'#{self.tag.name}'

        # Рекомендуемые пользователи как в PostListView
        if self.request.user.is_authenticated:
            try:
                subscribed_to = Subscription.objects.filter(
                    subscriber=self.request.user
                ).values_list('author_id', flat=True)

                context['suggested_users'] = User.objects.exclude(
                    id__in=list(subscribed_to) + [self.request.user.id]
                ).annotate(
                    subscribers_count=Count('subscribers')
                ).order_by('-subscribers_count')[:3]
            except Exception as e:
                context['suggested_users'] = []
                print(f"Error getting suggested users: {e}")

        # Добавляем популярные теги
        context['popular_tags'] = Tag.get_popular_tags()
        return context

def terms_of_use(request):
    return render(request, 'posts/terms_of_use.html')

def privacy_policy(request):
    return render(request, 'posts/privacy_policy.html')