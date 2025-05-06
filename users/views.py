# users/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model


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