import google.generativeai as genai
from django.conf import settings
from django.db.models import Count, Q
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


def get_gemini_response(prompt: str) -> str:
    """
    Отправляет запрос к Google Gemini API и возвращает текстовый ответ.
    """
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        logger.error("GOOGLE_API_KEY не настроен в settings.py.")
        return "Ошибка: Ключ API для сервиса ИИ не настроен."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    try:
        response = model.generate_content(prompt)
        if response.parts:
            return "".join(part.text for part in response.parts if hasattr(part, 'text'))
        elif hasattr(response, 'text') and response.text:
            return response.text
        else:
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                return "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
            return "ИИ не смог сгенерировать ответ в ожидаемом формате."

    except Exception as e:
        logger.error(f"Ошибка при взаимодействии с Gemini API: {e}")
        return f"Произошла ошибка при обращении к сервису ИИ. Подробности: {str(e)}"


def get_faq_answer(question: str, user_info: dict) -> str:
    """Отвечает на часто задаваемые вопросы о сайте."""
    prompt = f"""Пользователь {user_info.get('username', 'аноним')} задает вопрос о сайте Chatty Orange: '{question}'. 

    Chatty Orange - это социальная сеть со следующими функциями:
    - Создание постов с изображениями и тегами
    - Лайки и комментарии к постам
    - Система подписок на других пользователей
    - Персонализированная лента постов
    - Поиск по контенту и пользователям
    - Настройка профиля с аватаром

    Ответь на вопрос подробно и дружелюбно. Если вопрос не по теме сайта, вежливо укажи на это."""
    return get_gemini_response(prompt)


def get_feature_explanation(feature_query: str, user_info: dict) -> str:
    """Объясняет, как работают функции сайта."""
    prompt = f"""Пользователь {user_info.get('username', 'аноним')} спрашивает о функции '{feature_query}' на сайте Chatty Orange. 

    Подробно объясни:
    1. Что это за функция
    2. Как ею пользоваться (пошагово)
    3. Какие преимущества она дает
    4. Полезные советы по использованию

    Если функция неизвестна, предположи наиболее подходящую по контексту."""
    return get_gemini_response(prompt)


def get_interactive_tour_step(step_number: int, user_info: dict) -> str:
    """Возвращает контент для шага интерактивного тура."""
    tour_steps = {
        1: {
            "title": "🎉 Добро пожаловать в Chatty Orange!",
            "content": """Привет! Я твой Апельсиновый Помощник 🍊

            Chatty Orange - это уютная социальная сеть, где ты можешь:
            • Делиться мыслями и фотографиями
            • Находить друзей по интересам
            • Общаться в комментариях
            • Следить за обновлениями любимых авторов

            Готов узнать больше? Нажми "Далее"!"""
        },
        2: {
            "title": "✍️ Создание постов",
            "content": """Чтобы создать свой первый пост:

            1. Нажми кнопку "Создать пост" в навигации
            2. Напиши что-нибудь интересное
            3. Добавь фото (до 10 штук!)
            4. Выбери подходящие теги
            5. Нажми "Опубликовать"

            💡 Совет: Я могу помочь с идеями для поста!"""
        },
        3: {
            "title": "💬 Взаимодействие",
            "content": """Как общаться на Chatty Orange:

            ❤️ Лайки - нажми на сердечко под постом
            💬 Комментарии - поделись мнением
            🔄 Подписки - следи за интересными авторами
            📰 Лента - все посты от твоих подписок

            Чем активнее ты участвуешь, тем интереснее становится!"""
        },
        4: {
            "title": "🎯 Полезные функции",
            "content": """Дополнительные возможности:

            🔍 Поиск - найди посты и людей по интересам
            🏷️ Теги - фильтруй контент по темам
            👤 Профиль - настрой аватар и описание
            🍊 Я, твой помощник - всегда готов помочь!

            Поздравляю! Теперь ты готов к использованию Chatty Orange! 🎉"""
        }
    }

    step_data = tour_steps.get(step_number, tour_steps[4])
    return f"<h5>{step_data['title']}</h5>{step_data['content']}"


def get_post_creation_suggestion(current_text: str, user_info: dict) -> str:
    """Помогает с созданием поста."""
    if not current_text:
        prompt = f"""Пользователь {user_info.get('username', 'Аноним')} создает свой первый пост на Chatty Orange.

        Предложи 5 интересных идей для первого поста в формате:

        🌟 **Идея 1: [Название]**
        [Краткое описание и пример начала поста]

        Идеи должны быть разнообразными: приветствие, хобби, интересный факт, вопрос сообществу, фото-история."""
    else:
        prompt = f"""Пользователь {user_info.get('username', 'Аноним')} пишет пост:
        "{current_text}"

        Дай конструктивные советы:
        1. Что можно добавить или улучшить
        2. Какие теги подойдут
        3. Предложи интересное продолжение

        Будь дружелюбным и поддерживающим!"""

    return get_gemini_response(prompt)


def get_subscription_recommendations(user_info: dict, current_user_id: int = None) -> str:
    """Рекомендует интересных авторов для подписки."""
    from django.db.models import Count
    from users.models import CustomUser
    from posts.models import Post

    try:
        # Получаем популярных авторов
        recommended_users = CustomUser.objects.annotate(
            num_subscribers=Count('subscribers'),
            num_posts=Count('posts')
        ).filter(
            num_posts__gt=0  # Только те, кто писал посты
        ).order_by('-num_subscribers', '-num_posts')

        if current_user_id:
            recommended_users = recommended_users.exclude(id=current_user_id)
            # Исключаем тех, на кого уже подписан
            user = CustomUser.objects.get(id=current_user_id)
            subscribed_ids = user.subscriptions.values_list('target_id', flat=True)
            recommended_users = recommended_users.exclude(id__in=subscribed_ids)

        recommended_users = recommended_users[:5]

        if not recommended_users:
            return "🍊 Пока что мало активных авторов, но скоро их станет больше! А пока создай свой первый пост!"

        authors_info = []
        for user in recommended_users:
            # Получаем последний пост для контекста
            last_post = user.posts.order_by('-created_at').first()
            post_preview = f"Последний пост: {last_post.title[:30]}..." if last_post else "Еще нет постов"

            authors_info.append(f"""
🔸 **@{user.username}** ({user.num_subscribers} подписчиков, {user.num_posts} постов)
{f'📝 О себе: {user.bio[:100]}...' if user.bio else ''}
📰 {post_preview}""")

        recommendations = "\n".join(authors_info)

        return f"""🌟 **Рекомендую подписаться на этих интересных авторов:**

{recommendations}

💡 **Совет:** Подписывайся на авторов с похожими интересами, чтобы твоя лента была интересной!"""

    except Exception as e:
        logger.error(f"Ошибка при получении рекомендаций: {e}")
        return "Не удалось загрузить рекомендации. Попробуй позже! 🍊"


def check_post_content(post_text: str, user_info: dict) -> str:
    """Проверяет текст поста на соответствие правилам."""
    if not post_text.strip():
        return "📝 Текст поста не может быть пустым!"

    site_rules = """
    1. ❌ Запрещены оскорбления, угрозы и агрессия
    2. ❌ Запрещен контент 18+, насилие, шок-контент
    3. ❌ Запрещен спам и несогласованная реклама
    4. ❌ Запрещено разжигание ненависти
    5. ❌ Запрещены политика и религиозные споры
    6. ✅ Приветствуется оригинальный контент
    7. ✅ Основной язык - русский
    """

    prompt = f"""Проверь текст поста от {user_info.get('username', 'Аноним')}:
    "{post_text}"

    Правила Chatty Orange:
    {site_rules}

    Если всё хорошо, ответь: "✅ Отличный пост! Можно публиковать!"

    Если есть нарушения:
    1. Укажи конкретное нарушение
    2. Объясни, почему это нарушение
    3. Предложи, как исправить

    Будь дружелюбным и конструктивным!"""

    return get_gemini_response(prompt)


def analyze_profile_stats(user_id: int) -> str:
    """Анализирует статистику профиля и дает советы."""
    from users.models import CustomUser
    from posts.models import Post, Comment
    from subscriptions.models import Subscription

    try:
        user = CustomUser.objects.get(id=user_id)

        # Собираем статистику
        stats = {
            'posts_count': user.posts.count(),
            'comments_count': Comment.objects.filter(author=user).count(),
            'likes_received': sum(post.likes.count() for post in user.posts.all()),
            'subscribers_count': user.subscribers.count(),
            'subscriptions_count': user.subscriptions.count(),
            'days_on_site': (datetime.now().date() - user.created_at.date()).days
        }

        # Последняя активность
        last_post = user.posts.order_by('-created_at').first()
        last_comment = Comment.objects.filter(author=user).order_by('-created_at').first()

        prompt = f"""Проанализируй статистику пользователя @{user.username} на Chatty Orange:

        📊 Статистика:
        - Дней на сайте: {stats['days_on_site']}
        - Постов: {stats['posts_count']}
        - Комментариев: {stats['comments_count']}
        - Получено лайков: {stats['likes_received']}
        - Подписчиков: {stats['subscribers_count']}
        - Подписок: {stats['subscriptions_count']}

        Дай персонализированные советы:
        1. Оцени активность (низкая/средняя/высокая)
        2. Что делает хорошо
        3. Что можно улучшить
        4. 3 конкретных совета для роста

        Используй эмодзи и будь позитивным!"""

        return get_gemini_response(prompt)

    except Exception as e:
        logger.error(f"Ошибка анализа профиля: {e}")
        return "Не удалось проанализировать профиль. Попробуй позже! 🍊"


def generate_post_ideas(user_info: dict, tags: list = None) -> str:
    """Генерирует идеи для постов на основе трендов и интересов."""
    # Здесь можно анализировать популярные теги и темы
    available_tags = ['Путешествия', 'Еда', 'Технологии', 'Творчество', 'Спорт', 'Книги', 'Музыка', 'Фото']

    if tags:
        focus_tags = ', '.join(tags)
    else:
        focus_tags = 'разные темы'

    prompt = f"""Сгенерируй 5 креативных идей для постов в Chatty Orange для пользователя {user_info.get('username', 'Аноним')}.

    Тематика: {focus_tags}
    Доступные теги: {', '.join(available_tags)}

    Формат ответа:
    💡 **Идея 1: [Заголовок]**
    📝 Описание: [Что написать]
    📸 Фото: [Что сфотографировать]
    🏷️ Теги: [Подходящие теги]

    Идеи должны быть:
    - Интересными и вовлекающими
    - Легкими в реализации
    - Подходящими для социальной сети"""

    return get_gemini_response(prompt)


def analyze_sentiment(text: str) -> str:
    """Анализирует эмоциональный тон текста."""
    prompt = f"""Проанализируй эмоциональный тон этого текста:
    "{text}"

    Определи:
    1. Общее настроение (позитивное/нейтральное/негативное)
    2. Основные эмоции
    3. Уровень энергии (спокойный/умеренный/энергичный)

    Ответь кратко с использованием эмодзи:
    Настроение: [эмодзи] [описание]
    Эмоции: [список]
    Энергия: [уровень]"""

    return get_gemini_response(prompt)