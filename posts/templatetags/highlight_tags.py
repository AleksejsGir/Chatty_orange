from django import template
from django.utils.html import mark_safe
import re

register = template.Library()


@register.filter(name='highlight')
def highlight(text, query):
    if not query or not text:
        return text

    # Игнорировать запросы из одной буквы (кроме цифр)
    if len(query) == 1 and not query.isdigit():
        return text

    # Разбиваем на слова (игнорируя одиночные буквы)
    words = [word for word in re.findall(r'\b\w+\b', query) if len(word) > 1 or word.isdigit()]

    highlighted = str(text)
    for word in words:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        highlighted = pattern.sub(
            lambda m: f'<span class="highlight">{m.group(0)}</span>',
            highlighted
        )
    return mark_safe(highlighted)