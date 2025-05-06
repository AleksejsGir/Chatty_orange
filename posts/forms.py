from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Минимум 5 символов'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Минимум 20 символов'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-file'
            })
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError("Слишком короткий заголовок!")
        return title

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 20:
            raise forms.ValidationError("Пост должен содержать минимум 20 символов")
        return text

# <!-- TODO: Добавить валидацию для изображения (размер/формат) -->