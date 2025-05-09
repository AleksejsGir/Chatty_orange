# posts/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.views.generic.detail import SingleObjectMixin
from django.views import View
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.db.models import Count


class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    ordering = ['-pub_date'] # Используем правильное поле даты
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # Аннотируем количеством комментариев
        # Используем related_name 'comments' из модели Comment
        queryset = queryset.annotate(
            num_comments=Count('comments', distinct=True)
        )
        # Предзагружаем автора для эффективности
        queryset = queryset.select_related('author')
        return queryset


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