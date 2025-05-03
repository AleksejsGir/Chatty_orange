# users/views.py
from django.shortcuts import render

def home_page_view(request):
    context = {}
    return render(request, 'home.html', context)