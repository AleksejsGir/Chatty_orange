# posts/views.py
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Count, Q
from django.views.generic.detail import SingleObjectMixin
from django.views import View

from .models import Post, Comment, Tag, PostImage
from .forms import PostForm, CommentForm, PostImageFormSet
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
        # self.search_query = self.request.GET.get('q', '').strip()
        # Инициализация атрибутов по умолчанию
        self.search_query = self.request.GET.get('q', '').strip()
        self.search_terms = self.search_query.split() if self.search_query else []

        # Поиск по ID если введены только цифры
        if self.search_query.isdigit():
            return queryset.filter(pk=int(self.search_query))

        # Основная логика поиска
        if self.search_query:
            search_terms = self.search_query.split()
            found = False
            current_terms = search_terms.copy()
            queryset = Post.objects.none()  # Начинаем с пустого queryset

            # Поиск фразы с уменьшением слов
            while len(current_terms) > 0:
                phrase = ' '.join(current_terms)
                phrase_query = Q(title__icontains=phrase) | Q(text__icontains=phrase)
                qs = Post.objects.filter(phrase_query)

                if qs.exists():
                    queryset = qs
                    found = True
                    break
                else:
                    current_terms.pop()

            # Если фраза не найдена - ищем отдельные слова
            if not found:
                query = Q()
                for term in search_terms:
                    if len(term) > 1 or term.isdigit():
                        query |= Q(title__icontains=term) | Q(text__icontains=term)
                queryset = Post.objects.filter(query).distinct()

        # Аннотации и сортировка
        user = self.request.user
        annotation_filter = Q() if user.is_staff else Q(comments__is_active=True)

        return queryset.annotate(
            num_comments=Count('comments', filter=annotation_filter, distinct=True),
            num_likes=Count('likes', distinct=True),
            num_dislikes=Count('dislikes', distinct=True)
        ).select_related('author').order_by('-pub_date')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'current_filter': self.request.GET.get('filter', 'latest'),
            'popular_tags': Tag.get_popular_tags(),
            'search_query': self.search_query,
            'search_terms': self.search_terms
        })

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = PostImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['image_formset'] = PostImageFormSet()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        context = self.get_context_data()
        image_formset = context['image_formset']

        if image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = PostImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            context['image_formset'] = PostImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']

        if image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

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

class TermsOfUseView(TemplateView):
    template_name = 'terms_of_use.html'

class PrivacyPolicyView(TemplateView):
    template_name = 'privacy_policy.html'

def feed_view(request):
    posts = Post.objects.annotate(
        num_likes=Count('likes', distinct=True),
        total_dislikes=Count('dislikes', distinct=True),
        num_comments=Count('comments', distinct=True)
    )