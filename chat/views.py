# chat/views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, FormView

from .forms import MessageForm
from .models import Message

User = get_user_model()

class ChatListView(LoginRequiredMixin, ListView):
    template_name = 'chat/chat_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        user = self.request.user
        sent_to = Message.objects.filter(sender=user).values_list('recipient', flat=True)
        received_from = Message.objects.filter(recipient=user).values_list('sender', flat=True)
        user_ids = set(sent_to) | set(received_from)
        return User.objects.filter(id__in=user_ids)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Собираем пары (user, unread_count)
        chats = []
        for u in ctx['users']:
            unread = Message.objects.filter(
                sender=u,
                recipient=self.request.user,
                is_read=False
            ).count()
            chats.append({'user': u, 'unread': unread})
        ctx['chats'] = chats
        return ctx

class ChatDetailView(LoginRequiredMixin, FormView, ListView):
    template_name = 'chat/chat_detail.html'
    form_class = MessageForm
    context_object_name = 'messages'

    def dispatch(self, request, *args, **kwargs):
        self.interlocutor = get_object_or_404(User, username=kwargs['username'])
        Message.objects.filter(
            sender=self.interlocutor,
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        other = self.interlocutor
        return Message.objects.filter(
            Q(sender=user, recipient=other) |
            Q(sender=other, recipient=user)
        ).order_by('timestamp')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['interlocutor'] = self.interlocutor
        return ctx

    def form_valid(self, form):
        msg = form.save(commit=False)
        msg.sender = self.request.user
        msg.recipient = self.interlocutor
        msg.save()
        return redirect(reverse('chat:chat_detail', kwargs={
            'username': self.interlocutor.username
        }))
