from django.urls import path
from feedback.views import FeedbackView

urlpatterns = [
    path('feedback/<str:feedback_type>/', FeedbackView.as_view(), name='feedback-form'),
]