from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag('posts/components/back_button.html', takes_context=True)
def back_button(context, post=None):
    request = context['request']
    referer = request.META.get('HTTP_REFERER', '')
    from_param = request.GET.get('from')

    url = reverse('posts:post-list')
    label = 'Назад'
    btn_class = 'btn btn-outline-secondary'

    #  from=created — приоритет!
    if from_param == 'created':
        label = 'Перейти в ленту'
        btn_class = 'btn-outline-secondary'
        return {'url': url, 'label': label, 'btn_class': btn_class}

    #  Теперь можно использовать referer
    if referer:
        return {'url': referer, 'label': label, 'btn_class': btn_class}

    #  Остальные случаи
    if from_param == 'subscriptions':
        url = reverse('posts:post-list') + '?filter=subscriptions'
    elif from_param == 'popular':
        url = reverse('posts:post-list') + '?filter=popular'
    elif from_param == 'profile' and post:
        url = reverse('users:profile', args=[post.author.username])
    elif from_param == 'tag' and post and post.tags.exists():
        url = reverse('posts:tag-posts', args=[post.tags.first().slug])

    return {
        'url': url,
        'label': label,
        'btn_class': btn_class,
    }