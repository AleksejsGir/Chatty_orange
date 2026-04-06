# from django import template
# from django.urls import reverse
#
# register = template.Library()
#
# @register.inclusion_tag('posts/components/back_button.html', takes_context=True)
# def back_button(context, post=None):
#     request = context['request']
#     referer = request.META.get('HTTP_REFERER', '')
#     # Смотрим сначала в POST (удаление комментария), потом в GET (создание, клик из ленты и т.д.)
#     from_param = request.POST.get('from') or request.GET.get('from')
#
#     # Базовая лента
#     url = reverse('posts:post-list')
#     label = 'Назад'
#     btn_class = 'btn btn-outline-secondary'
#
#     # 1) Если from=created — это после создания самого поста
#     if from_param == 'created':
#         label = 'Перейти в ленту'
#         btn_class = 'btn btn-outline-secondary'
#         return {'url': url, 'label': label, 'btn_class': btn_class}
#
#     # 2) Остальные специальные from‑значения
#     if from_param == 'latest':
#         return {'url': url, 'label': label, 'btn_class': btn_class}
#
#     if from_param == 'subscriptions':
#         url = reverse('posts:post-list') + '?filter=subscriptions'
#         return {'url': url, 'label': label, 'btn_class': btn_class}
#
#     if from_param == 'popular':
#         url = reverse('posts:post-list') + '?filter=popular'
#         return {'url': url, 'label': label, 'btn_class': btn_class}
#
#     if from_param == 'profile' and post:
#         url = reverse('users:profile', args=[post.author.username])
#         return {'url': url, 'label': label, 'btn_class': btn_class}
#
#     if from_param == 'tag' and post and post.tags.exists():
#         url = reverse('posts:tag-posts', args=[post.tags.first().slug])
#         return {'url': url, 'label': label, 'btn_class': btn_class}
#
#     # 3) Если from_param нет, но есть referer — возвращаем туда (например, кликнули «назад» из браузера)
#     if referer:
#         return {'url': referer, 'label': label, 'btn_class': btn_class}
#
#     # 4) По умолчанию — в общую ленту
#     return {'url': url, 'label': label, 'btn_class': btn_class}
#
from django import template
from django.urls import reverse

register = template.Library()

@register.inclusion_tag('posts/components/back_button.html', takes_context=True)
def back_button(context, post=None, extra_class=''):
    request = context['request']
    referer = request.META.get('HTTP_REFERER', '')
    from_param = request.POST.get('from') or request.GET.get('from')

    url = reverse('posts:post-list')
    label = 'Назад'
    btn_class = 'btn btn-outline-secondary'

    if from_param == 'created':
        label = 'Перейти в ленту'
        return {'url': url, 'label': label, 'btn_class': btn_class, 'extra_class': extra_class}

    if from_param == 'latest':
        return {'url': url, 'label': label, 'btn_class': btn_class, 'extra_class': extra_class}

    if from_param == 'subscriptions':
        url = reverse('posts:post-list') + '?filter=subscriptions'
    elif from_param == 'popular':
        url = reverse('posts:post-list') + '?filter=popular'
    elif from_param == 'profile' and post:
        url = reverse('users:profile', args=[post.author.username])
    elif from_param == 'tag' and post and post.tags.exists():
        url = reverse('posts:tag-posts', args=[post.tags.first().slug])

    elif referer:
        return {'url': referer, 'label': label, 'btn_class': btn_class, 'extra_class': extra_class}

    return {'url': url, 'label': label, 'btn_class': btn_class, 'extra_class': extra_class}
