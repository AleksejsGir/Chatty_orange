# chat/context_processors.py
from .models import Message

def unread_message_count(request):
    if request.user.is_authenticated:
        count = Message.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
    else:
        count = 0
    return {'unread_message_count': count}
