# orange_assistant/urls.py
from django.urls import path
from .views import ChatWithAIView

app_name = 'orange_assistant'

urlpatterns = [
    path('api/chat/', ChatWithAIView.as_view(), name='ai_chat'),
]
