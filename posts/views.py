from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post
from .forms import PostForm

from django.contrib.auth.mixins import UserPassesTestMixin

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = '/posts/'

    def form_valid(self, form):
        form.instance.author = self.request.user  # Автоматическая привязка автора
        return super().form_valid(form)

class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = ['-pub_date']  # Сортировка по дате

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    slug_field = 'slug'  # Для работы с ЧПУ
    slug_url_kwarg = 'slug'

# class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = Post
#     form_class = PostForm
#     template_name = 'posts/post_form.html'
#
#     def test_func(self):
#         return self.get_object().author == self.request.user  # Проверка авторства
#
# class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#     model = Post
#     success_url = '/posts/'
#
#     def test_func(self):
#         return self.get_object().author == self.request.user