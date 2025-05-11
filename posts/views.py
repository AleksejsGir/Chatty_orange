# posts/views.py
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.views.generic.detail import SingleObjectMixin
from django.views import View
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Count
from subscriptions.models import Subscription  # Добавляем импорт модели подписок

User = get_user_model()  # Получаем модель пользователя


class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Аннотируем количеством комментариев и лайков
        queryset = queryset.annotate(
            num_comments=Count('comments', distinct=True),
            num_likes=Count('likes', distinct=True)
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
        context['comments'] = self.object.comments.all().order_by('-created_at')

        # Пагинация комментариев
        comments = self.object.comments.all().order_by('created_at')
        paginator = Paginator(comments, self.paginate_comments_by)
        page_number = self.request.GET.get('comment_page')
        context['comments'] = paginator.get_page(page_number)

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


@method_decorator(csrf_exempt, name='dispatch')
class PostLikeView(LoginRequiredMixin, View):
    """Обработка лайков через AJAX."""

    def post(self, request, *args, **kwargs):
        print("Like view called")  # Отладочное сообщение
        post_id = kwargs.get('pk')
        try:
            post = Post.objects.get(pk=post_id)
            user = request.user

            if post.likes.filter(id=user.id).exists():
                post.likes.remove(user)
                liked = False
                print(f"User {user} unliked post {post_id}")
            else:
                post.likes.add(user)
                liked = True
                print(f"User {user} liked post {post_id}")

            return JsonResponse({
                'status': 'ok',
                'liked': liked,
                'total_likes': post.total_likes()
            })
        except Post.DoesNotExist:
            print(f"Post {post_id} not found")
            return JsonResponse({
                'status': 'error',
                'message': 'Post not found'
            }, status=404)
        except Exception as e:
            print(f"Error in like view: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)