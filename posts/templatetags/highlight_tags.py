from django import template
from django.utils.html import mark_safe
import re

register = template.Library()


@register.filter
def highlight(text, query):
    if not query or not text:
        return text

    words = re.findall(r'\w+', query)
    highlighted = str(text)
    for word in words:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        highlighted = pattern.sub(
            lambda m: f'<span class="highlight">{m.group(0)}</span>',
            highlighted
        )
    return mark_safe(highlighted)