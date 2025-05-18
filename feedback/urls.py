from django.urls import path
from .views import FeedbackView

app_name = 'feedback'  # Это важно для пространства имен

urlpatterns = [
    path('<str:feedback_type>/', FeedbackView.as_view(), name='feedback-form'),
]