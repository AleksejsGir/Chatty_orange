# posts/views.py

from django.views.generic import CreateView, ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Post
from .forms import PostForm

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('posts:post_list')  # или другой маршрут

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

# Пример для UserPassesTestMixin — для редактирования или удаления
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostForm

    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('posts:post-list')


    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('posts:post-list')

    def test_func(self):
        return self.request.user == self.get_object().author








#
#
# from django.shortcuts import render
# from django.views.generic import CreateView, ListView, DetailView
# from django.views.generic.edit import UpdateView
# from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# from django.urls import reverse_lazy
# from .models import Post
# from .forms import PostForm
#
#
# class PostCreateView(LoginRequiredMixin, CreateView):
#     model = Post
#     form_class = PostForm
#     template_name = 'posts/post_create.html'
#
#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return reverse_lazy('post-list')
#
#
# class PostListView(ListView):
#     model = Post
#     template_name = 'posts/post_list.html'
#     context_object_name = 'posts'
#     ordering = ['-created_at']
#
#
# class PostDetailView(DetailView):
#     model = Post
#     template_name = 'posts/post_detail.html'
#     context_object_name = 'post'
#
#
# class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = Post
#     form_class = PostForm
#     template_name = 'posts/post_edit.html'
#
#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return reverse_lazy('post-detail', kwargs={'pk': self.object.pk})
#
#     def test_func(self):
#         post = self.get_object()
#         return post.author == self.request.user
#
#
#
#
