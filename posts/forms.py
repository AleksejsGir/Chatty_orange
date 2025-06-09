# posts/forms.py
from django import forms
from django.template.defaultfilters import slugify
from django.forms import inlineformset_factory

from .models import Post, Comment, PostImage
from ckeditor.widgets import CKEditorWidget

from django.utils.text import slugify
from django.core.exceptions import ValidationError

class PostForm(forms.ModelForm):
    agree_to_rules = forms.BooleanField(
        label="Я согласен с правилами публикации контента",
        required=True,
        error_messages={'required': 'Вы должны принять правила публикации'}
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок'
            }),
            # Виджет CKEditor будет подключен автоматически, так как мы используем RichTextField в модели
            # Если нужно дополнительно настроить, можно добавить:
            # 'text': CKEditorWidget(config_name='default'),
            'tags': forms.CheckboxSelectMultiple(attrs={
                'class': 'tag-checkbox-list'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError("Заголовок должен содержать минимум 5 символов")
        return title

    def clean_text(self):
        text = self.cleaned_data['text']

        # Проверка на минимальную длину
        if len(text) < 10:
            raise ValidationError("Текст поста должен содержать минимум 10 символов")

        # Проверка на запрещенные слова
        bad_words = ['мат', 'оскорбление', 'запрещенное_слово']  # Замените на реальный список
        cleaned_text = slugify(text)  # Нормализуем текст для проверки

        for word in bad_words:
            if word in cleaned_text:
                raise ValidationError("Обнаружена ненормативная лексика")

        return text

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        forbidden_tags = ['политика', 'религия']
        for tag in tags:
            if tag.name.lower() in forbidden_tags:
                raise forms.ValidationError(
                    f"Тег '{tag.name}' запрещен к использованию"
                )
        return tags

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш комментарий...',
                'rows': 3
            })
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text) < 3:
            raise forms.ValidationError("Комментарий должен содержать минимум 3 символа")
        return text

# Добавляем форму для изображений
class PostImageForm(forms.ModelForm):
    class Meta:
        model = PostImage
        fields = ['image', 'order']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/jpeg,image/png'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            })
        }

# Создаем формсет для работы с несколькими изображениями
PostImageFormSet = inlineformset_factory(
    Post,
    PostImage,
    form=PostImageForm,
    extra=0,  # Количество дополнительных форм для новых изображений
    can_delete=True,  # Разрешить удаление изображений
    min_num=0,
    max_num=10  # Максимальное количество изображений
)