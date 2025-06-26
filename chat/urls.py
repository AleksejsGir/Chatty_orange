# chat/urls.py
from django.urls import path
from .views import (
    ChatListView, ChatDetailView,
    MessageUpdateView, MessageDeleteView
)

app_name = 'chat'

urlpatterns = [
    # Список всех диалогов у текущего пользователя
    path('', ChatListView.as_view(), name='chat_list'),
    # Конкретный диалог с пользователем по username
    path('<str:username>/', ChatDetailView.as_view(), name='chat_detail'),
    path('edit/<int:pk>/', MessageUpdateView.as_view(), name='message_edit'),
    path('delete/<int:pk>/', MessageDeleteView.as_view(), name='message_delete'),
]
