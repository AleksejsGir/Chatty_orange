# users/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import ProfileUpdateForm

CustomUser = get_user_model()

def home_page_view(request):
    context = {}
    return render(request, 'home.html', context)

def profile_view(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    context = {
        'profile_user': profile_user
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