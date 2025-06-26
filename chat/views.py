# chat/views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, FormView
from django.views.generic.edit import UpdateView, DeleteView
from django.utils import timezone
from django.contrib import messages

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
        # время последнего сообщения от текущего пользователя к собеседнику
        last = Message.objects.filter(
            sender=self.request.user,
            recipient=self.interlocutor
        ).order_by('-timestamp').first()
        ctx['last_ts'] = int(last.timestamp.timestamp()) if last else 0
        return ctx

    def form_valid(self, form):
        # антиспам: проверяем время последнего сообщения
        last = Message.objects.filter(
            sender=self.request.user,
            recipient=self.interlocutor
        ).order_by('-timestamp').first()

        if last and (timezone.now() - last.timestamp).total_seconds() < 2:
            messages.error(self.request,
                           'Пожалуйста, подождите несколько секунд перед следующим сообщением.')
            return self.form_invalid(form)

        msg = form.save(commit=False)
        msg.sender = self.request.user
        msg.recipient = self.interlocutor
        msg.save()
        return redirect(reverse('chat:chat_detail', kwargs={
            'username': self.interlocutor.username
        }))

class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'chat/message_edit.html'

    def get_queryset(self):
        # Редактировать может только автор
        return Message.objects.filter(sender=self.request.user)

    def get_success_url(self):
        # После редактирования возвращаемся в чат
        return reverse('chat:chat_detail', kwargs={
            'username': self.object.recipient.username
        })

class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'chat/message_confirm_delete.html'

    def get_queryset(self):
        # Удалять может только автор
        return Message.objects.filter(sender=self.request.user)

    def get_success_url(self):
        # После удаления — обратно в чат
        other = self.object.recipient
        return reverse_lazy('chat:chat_detail', kwargs={
            'username': other.username
        })