# posts/views.py
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_POST
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
from django.core.mail import send_mail
import json

from .models import CommentReaction
from .models import Post, Comment, Tag
from .forms import PostForm, CommentForm, PostImageFormSet
from subscriptions.models import Subscription

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

User = get_user_model()

class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        # Инициализация атрибутов для поиска по умолчанию
        self.search_query = self.request.GET.get('q', '').strip()
        self.search_terms = []

        # Базовый запрос с предварительной загрузкой автора и аннотациями
        queryset = Post.objects.select_related('author').annotate(
            num_comments=Count('comments', filter=Q(comments__is_active=True, comments__parent=None) | Q(comments__isnull=True), distinct=True),
            num_likes=Count('likes', distinct=True),
            num_dislikes=Count('dislikes', distinct=True)
        )

        # Логика поиска
        if self.search_query:
            if self.search_query.isdigit():
                # Поиск по ID, если введены только цифры
                # Этот результат является окончательным, остальные фильтры не применяются
                self.search_terms = []  # ID поиск не использует search_terms в шаблоне
                return queryset.filter(pk=int(self.search_query))
            else:
                # Текстовый поиск
                self.search_terms = self.search_query.split()
                search_query_obj = Q()
                # Поиск по целой фразе
                search_query_obj |= Q(title__icontains=self.search_query)
                search_query_obj |= Q(text__icontains=self.search_query)

                # Поиск по отдельным словам (если фраза не дала результатов или для расширения)
                # Можно добавить более сложную логику, как была ранее, если потребуется
                # Например, поиск по всем словам, или по части слов.
                # Текущая реализация ищет фразу целиком ИЛИ отдельные слова.
                for term in self.search_terms:
                    if len(term) > 1:  # Игнорируем слишком короткие слова
                        search_query_obj |= Q(title__icontains=term)
                        search_query_obj |= Q(text__icontains=term)

                queryset = queryset.filter(search_query_obj).distinct()

        # Логика фильтрации (применяется к результатам поиска или ко всем постам)
        filter_param = self.request.GET.get('filter', 'latest')

        if filter_param == 'subscriptions':
            if self.request.user.is_authenticated:
                subscribed_author_ids = Subscription.objects.filter(
                    subscriber=self.request.user
                ).values_list('author_id', flat=True)
                queryset = queryset.filter(author_id__in=subscribed_author_ids).order_by('-pub_date')
            else:
                queryset = Post.objects.none()
        elif filter_param == 'popular':
            queryset = queryset.order_by('-num_likes', '-pub_date')
        else:  # 'latest' или любой другой/не указанный параметр
            queryset = queryset.order_by('-pub_date')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'current_filter': self.request.GET.get('filter', 'latest'),
            'popular_tags': Tag.get_popular_tags(),
            'search_query': getattr(self, 'search_query', ''),
            'search_terms': getattr(self, 'search_terms', [])
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
    paginate_comments_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()

        user = self.request.user
        if user.is_staff:
            comments_qs = self.object.comments.filter(parent=None).annotate(
                replies_count=Count('replies', filter=Q(replies__is_active=True))
            ).order_by('-created_at')
        else:
            comments_qs = self.object.comments.filter(parent=None, is_active=True).annotate(
                replies_count=Count('replies', filter=Q(replies__is_active=True))
            ).order_by('-created_at')

        # Пагинация комментариев
        paginator = Paginator(comments_qs, self.paginate_comments_by)
        page_number = self.request.GET.get('comment_page')
        context['comments'] = paginator.get_page(page_number)

        context['popular_tags'] = Tag.get_popular_tags()

        # Добавляем подсчёт общего количества ответов
        context['root_comments_count'] = comments_qs.count()  # Только корневые
        post = self.object
        if self.request.user.is_staff:
            context['replies_count'] = post.comments.filter(parent__isnull=False).count()
        else:
            context['replies_count'] = post.comments.filter(parent__isnull=False, is_active=True).count()

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

            self.success_url = f"{self.object.get_absolute_url()}?from=created"

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

            # ✅ Сохраняем `from` и делаем редирект на пост с этим параметром
            from_param = self.request.GET.get('from') or self.request.POST.get('from')
            if from_param:
                return redirect(f"{self.object.get_absolute_url()}?from={from_param}")
            return redirect(self.object.get_absolute_url())

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
        self.object = self.get_object()            # пост, к которому добавляем комментарий
        form = self.form_class(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()

            # Сначала смотрим в POST, потом в GET
            from_param = request.POST.get('from') or request.GET.get('from')
            if from_param:
                return redirect(f"{self.object.get_absolute_url()}?from={from_param}#comments")

            # Если from не передан, просто возвращаем на якорь #comments
            return redirect(self.object.get_absolute_url() + '#comments')

        # Если форма невалидна, показываем страницу с ошибками
        return self.render_to_response(
            self.get_context_data(post=self.object, comment_form=form)
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


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        post_url = self.object.post.get_absolute_url()
        from_param = request.POST.get('from') or request.GET.get('from')
        self.object.delete()

        if from_param:
            return redirect(f"{post_url}?from={from_param}#comments")
        return redirect(f"{post_url}#comments")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})

# posts/views.py (PostLikeView)
@method_decorator(ensure_csrf_cookie, name='dispatch')
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
@method_decorator(ensure_csrf_cookie, name='dispatch')
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

class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ['text']
    template_name = 'posts/comment_edit.html'

    def get_success_url(self):
        return self.object.post.get_absolute_url()

class CommentReplyView(View):
    def post(self, request, parent_id):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required'})
        parent_comment = Comment.objects.get(id=parent_id)
        comment_text = request.POST.get('text')
        new_comment = Comment.objects.create(
            author=request.user,
            text=comment_text,
            parent=parent_comment
        )
        html = render_to_string('posts/comment.html', {'comment': new_comment, 'level': parent_comment.level + 1})
        return JsonResponse({'success': True, 'html': html})

# Обработчик реакций
@require_POST
def comment_react(request, comment_id):
    try:
        # Читаем данные из тела запроса
        data = json.loads(request.body)
        emoji = data.get('emoji')
    except:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    if not emoji:
        return JsonResponse({'status': 'error', 'message': 'Emoji not provided'}, status=400)

    comment = get_object_or_404(Comment, id=comment_id)

    # Находим или создаем реакцию
    reaction, created = CommentReaction.objects.get_or_create(
        comment=comment,
        emoji=emoji
    )

    # Переключаем реакцию пользователя
    if request.user in reaction.users.all():
        reaction.users.remove(request.user)
        action = 'removed'
    else:
        reaction.users.add(request.user)
        action = 'added'

    # Получаем обновленные реакции
    reactions = []
    for r in comment.reactions.annotate(count=Count('users')):
        reactions.append({
            'emoji': r.emoji,
            'count': r.count,
            'user_reacted': request.user in r.users.all()
        })

    return JsonResponse({
        'status': 'success',
        'action': action,
        'reactions': reactions
    })

@csrf_exempt
def submit_advice(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if not all([name, email, message]):
            return JsonResponse({
                'status': 'error',
                'title': 'Ошибка',
                'message': 'Пожалуйста, заполните все поля',
                'icon': 'error'
            }, status=400)

        try:
            send_mail(
                f'Новый совет от {name}',
                f'Имя: {name}\nEmail: {email}\n\nСообщение:\n{message}',
                'noreply@chatty.com',
                ['chattyorangeeu@gmail.com'],
                fail_silently=False,
            )
            return JsonResponse({
                'status': 'success',
                'title': 'Успешно!',
                'message': 'Спасибо за ваш совет! Мы ценим ваше мнение.',
                'icon': 'success'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'title': 'Ошибка',
                'message': f'Произошла ошибка при отправке: {str(e)}',
                'icon': 'error'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'title': 'Ошибка',
        'message': 'Неверный метод запроса',
        'icon': 'error'
    }, status=400)

@require_POST
def edit_comment(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Требуется авторизация'}, status=403)

    try:
        comment = Comment.objects.get(pk=pk, author=request.user)
        data = json.loads(request.body)
        new_text = data.get('text', '')

        if new_text:
            comment.text = new_text
            comment.save()
            return JsonResponse({'status': 'success', 'text': comment.text})

        return JsonResponse({'status': 'error', 'message': 'Пустой текст'}, status=400)

    except Comment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Комментарий не найден'}, status=404)

@login_required
def user_reactions(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user_reactions = CommentReaction.objects.filter(
        comment=comment,
        users=request.user
    ).values_list('emoji', flat=True)
    return JsonResponse(list(user_reactions))

@require_POST
def comment_update(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if request.user != comment.author and not request.user.is_staff:
        return JsonResponse({'success': False}, status=403)

    new_text = request.POST.get('text', '').strip()

    if not new_text:
        return JsonResponse({'success': False, 'error': 'Текст не может быть пустым'}, status=400)

    comment.text = new_text
    comment.save()

    return JsonResponse({
        'success': True,
        'new_text': new_text
    })


@login_required
@require_POST
def toggle_reaction(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    emoji = request.POST.get('emoji')

    if not emoji:
        return JsonResponse({'status': 'error', 'message': 'Emoji not provided'})

    # Проверяем существующую реакцию текущего пользователя
    reaction = CommentReaction.objects.filter(
        comment=comment,
        user=request.user,
        emoji=emoji
    ).first()

    if reaction:
        # Удаляем реакцию, если она уже существует
        reaction.delete()
        action = 'removed'
    else:
        # Создаем новую реакцию
        CommentReaction.objects.create(
            comment=comment,
            user=request.user,
            emoji=emoji
        )
        action = 'added'

    # Получаем обновленные агрегированные реакции
    reactions = comment.reactions.values('emoji').annotate(count=Count('id')).order_by('-count')

    # Получаем ВСЕ реакции текущего пользователя для этого комментария
    user_reactions = comment.reactions.filter(
        user=request.user
    ).values_list('emoji', flat=True)

    return JsonResponse({
        'status': 'success',
        'action': action,
        'reactions': list(reactions),
        'user_reactions': list(user_reactions)
    })

@login_required
@require_POST
def comment_reply(request, parent_id):
    try:
        parent_comment = get_object_or_404(Comment, id=parent_id)
        comment_text = request.POST.get('text', '').strip()

        if not comment_text:
            return JsonResponse({
                'success': False,
                'error': 'Текст комментария не может быть пустым'
            })

        new_comment = Comment.objects.create(
            author=request.user,
            text=comment_text,
            parent=parent_comment,
            post=parent_comment.post,
            level=parent_comment.level + 1
        )

        # Рендерим комментарий с передачей request
        html = render_to_string('posts/comment.html', {
            'comment': new_comment,
            'level': parent_comment.level + 1,
            'request': request
        })

        return JsonResponse({
            'success': True,
            'html': html,
            'replies_count': parent_comment.replies.filter(is_active=True).count()
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        })