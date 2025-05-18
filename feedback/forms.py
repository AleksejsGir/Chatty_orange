from django import forms

class FeedbackForm(forms.Form):
    email = forms.EmailField(label='Ваш email', required=True)
    message = forms.CharField(
        label='Сообщение',
        widget=forms.Textarea(attrs={'rows': 5}),
        required=True
    )