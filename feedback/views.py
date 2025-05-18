from django.views.generic import FormView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect
from .forms import FeedbackForm


class FeedbackView(FormView):
    template_name = 'feedback/feedback_form.html'
    form_class = FeedbackForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        feedback_type = self.kwargs.get('feedback_type')

        if feedback_type == 'compliment':
            context['title'] = 'Жалобы и Благодарности'
        elif feedback_type == 'suggestion':
            context['title'] = 'Советы разработчикам'

        return context

    def form_valid(self, form):
        feedback_type = self.kwargs.get('feedback_type')
        subject = f"{self.get_context_data()['title']} от {form.cleaned_data['email']}"
        message = form.cleaned_data['message']

        send_mail(
            subject,
            message,
            'noreply@chatty.com',
            ['Chattyorangeeu@gmail.com'],
            fail_silently=False,
        )

        messages.success(self.request, 'Ваше сообщение успешно отправлено!')
        return super().form_valid(form)