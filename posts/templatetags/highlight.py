# templatetags/highlight.py
from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter
def highlight(text, query):
    if not query or not text:
        return text

    words = query.split()
    highlighted = str(text)

    # Сначала выделяем полную фразу
    highlighted = re.sub(
        f'({re.escape(query)})',
        r'<mark class="highlight">\1</mark>',
        highlighted,
        flags=re.IGNORECASE
    )

    # Затем выделяем отдельные слова
    for word in words:
        highlighted = re.sub(
            f'({re.escape(word)})',
            r'<mark class="highlight">\1</mark>',
            highlighted,
            flags=re.IGNORECASE
        )

    return mark_safe(highlighted)