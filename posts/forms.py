# posts/forms.py

from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Текст поста'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError("Заголовок должен быть не короче 5 символов.")
        return title






#
# from django import forms
# from .models import Post
#
#
# class PostForm(forms.ModelForm):
#     class Meta:
#         model = Post
#         fields = ['title', 'text', 'image']
#
#     # Настройка виджетов для полей
#     widgets = {
#         'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок'}),
#         'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите текст'}),
#         'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
#     }
#
#     # Валидация данных
#     def clean_title(self):
#         title = self.cleaned_data.get('title')
#         if len(title) < 5:
#             raise forms.ValidationError('Заголовок должен содержать минимум 5 символов.')
#         return title
# 
#     def clean_text(self):
#         text = self.cleaned_data.get('text')
#         if len(text) < 10:
#             raise forms.ValidationError('Текст должен содержать минимум 10 символов.')
#         return text
