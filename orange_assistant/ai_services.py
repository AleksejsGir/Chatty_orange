#import google.generativeai as genai
import google.genai as genai
from django.conf import settings
from django.db.models import Count, Q
import logging
from datetime import datetime, timedelta
import json

# Импортируем все модели глобально
from posts.models import Post, Comment
from users.models import CustomUser

# Импортируем модель подписок
try:
    from subscriptions.models import Subscription
except ImportError:
    logger.error("Модель Subscription не найдена")
    Subscription = None

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
    model = genai.GenerativeModel('gemini-2.0-flash')

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
    """Объясняет, как работают функции сайта, или общие возможности ассистента."""

    user_name = user_info.get('username', 'аноним')
    normalized_query = feature_query.lower()

    general_capability_keywords = [
        "что ты умеешь", "твои функции", "возможности",
        "хелп", "помощь", "что можешь", "расскажи о себе", "команды"
    ]

    is_general_query = any(keyword in normalized_query for keyword in general_capability_keywords)

    if is_general_query:
        prompt = f"""Пользователь {user_name} спрашивает о твоих общих возможностях или просит помощи.
Расскажи о себе и основных функциях сайта Chatty Orange, которые ты поддерживаешь.
Chatty Orange - это социальная сеть, где пользователи могут создавать посты, комментировать, подписываться на других и т.д.

Твои основные возможности:
- Ответы на вопросы о сайте (FAQ).
- Объяснение конкретных функций сайта.
- Помощь в создании постов (предложение идей, советы по улучшению).
- Рекомендации интересных авторов для подписки.
- Проверка текста поста на соответствие правилам сайта.
- Анализ статистики профиля пользователя и советы по его развитию.
- Генерация идей для новых постов.
- Анализ эмоционального тона текста.

Кстати, я также недавно научился новым трюкам:
- 🕵️ **Искать посты по ключевым словам.** Просто спроси: "Найди посты про [ключевое слово]". Например: "Найди посты про путешествия".
- 📄 **Показывать детали поста.** Если знаешь название поста, спроси: "Расскажи о посте [название]".
- 👤 **Находить пользователей.** Спроси: "Найди пользователя [имя пользователя]". Например: "Найди пользователя admin".
- 📊 **Показывать активность пользователя.** Спроси: "Что нового у [имя пользователя]?".

Представь эту информацию дружелюбно и структурированно. Поощряй пользователя задавать вопросы.
"""
    else:
        prompt = f"""Пользователь {user_name} спрашивает о функции '{feature_query}' на сайте Chatty Orange. 

        Подробно объясни:
        1. Что это за функция.
        2. Как ею пользоваться (пошагово).
        3. Какие преимущества она дает.
        4. Полезные советы по использованию.

        Если функция '{feature_query}' неизвестна или не является специфической функцией сайта, но ты можешь помочь с этим запросом (например, это общий вопрос или просьба), ответь наилучшим образом. 
        Если это похоже на запрос одной из твоих специальных возможностей (например, поиск постов, анализ текста), выполни его.
        Если это совершенно неизвестный запрос, вежливо сообщи, что ты не можешь помочь с этой конкретной темой, но готов помочь с другими вопросами о Chatty Orange."""

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

            👍 Лайки - нажми на палец вверх под постом
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
    content_html = step_data['content'].replace('\n', '<br>')
    return f"<h5>{step_data['title']}</h5><p>{content_html}</p>"


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


def find_post_by_keyword(keyword: str, user_info: dict) -> str:
    """
    Ищет посты по ключевому слову и представляет их пользователю без ID.
    """
    logger.info(f"Пользователь {user_info.get('username', 'аноним')} ищет посты с ключевым словом: '{keyword}'")
    try:
        # Проверяем, что модель Post доступна
        if Post is None:
            logger.error("Модель Post не доступна")
            return "Ошибка: модель постов не доступна. Обратитесь к администратору."

        # Выполняем поиск
        posts = Post.objects.filter(Q(title__icontains=keyword) | Q(text__icontains=keyword))[:10]

        logger.info(f"Найдено {posts.count()} постов по ключевому слову '{keyword}'")

        if not posts.exists():
            logger.info(f"Посты с ключевым словом '{keyword}' не найдены.")
            return f"К сожалению, посты с ключевым словом '{keyword}' не найдены. Попробуйте другой запрос."

        posts_info = []
        for post in posts:
            author_username = post.author.username if post.author else "неизвестный автор"
            try:
                post_url = post.get_absolute_url() if hasattr(post, 'get_absolute_url') else f"/posts/{post.id}/"
            except Exception as e:
                logger.warning(f"Ошибка при получении URL поста {post.id}: {e}")
                post_url = f"/posts/{post.id}/"

            # ИСПРАВЛЕНО: Возвращаем чистый текст БЕЗ HTML-тегов
            # JavaScript formatMessage сам создаст ссылки
            posts_info.append(
                f"• **{post.title}** от @{author_username}\n  Ссылка: {post_url}")

        posts_details_str = "\n\n".join(posts_info)

        return f"""🔍 **Найденные посты по запросу "{keyword}":**

{posts_details_str}

💡 Нажми на ссылку, чтобы прочитать пост полностью!"""

    except Exception as e:
        logger.error(f"Ошибка при поиске постов по ключевому слову '{keyword}': {e}")
        return f"Произошла ошибка при поиске постов: {str(e)} 🍊"


def get_post_details(post_id: int, user_info: dict) -> str:
    """
    Получает детали поста по его ID и представляет их без технических подробностей.
    """
    logger.info(f"Пользователь {user_info.get('username', 'аноним')} запрашивает детали поста с ID: {post_id}")
    try:
        # Проверяем доступность моделей
        if Post is None:
            return "Ошибка: модель постов не доступна."

        if Comment is None:
            return "Ошибка: модель комментариев не доступна."

        post = Post.objects.get(pk=post_id)
        author_username = post.author.username if post.author else "неизвестный автор"
        likes_count = post.likes.count() if hasattr(post, 'likes') else 0

        comments = Comment.objects.filter(post=post).order_by('-created_at')[:5]
        comments_info = []
        if comments:
            for comment in comments:
                comment_author = comment.author.username if comment.author else "аноним"
                comments_info.append(
                    f"💬 @{comment_author}: {comment.text[:100]}{'...' if len(comment.text) > 100 else ''}")
        else:
            comments_info.append("Комментариев пока нет.")

        comments_details_str = "\n".join(comments_info)

        # ИСПРАВЛЕНО: Убираем HTML-теги, возвращаем чистый текст
        # JavaScript formatMessage сам создаст ссылки из @username
        post_details = f"""
📰 **{post.title}**
✍️ Автор: @{author_username}
❤️ Лайков: {likes_count}

📝 **Содержание:**
{post.text[:500]}{'...' if len(post.text) > 500 else ''} 

💬 **Последние комментарии:**
{comments_details_str}
        """

        logger.info(f"Успешно получены детали для поста: {post.title}")

        return f"🎯 **Вот что я нашел:**{post_details}\n\n💡 Хочешь оставить свой комментарий или поставить лайк? Переходи к посту!"

    except Post.DoesNotExist:
        logger.warning(f"Пост с ID {post_id} не найден.")
        return f"К сожалению, пост не найден. Возможно, он был удален."
    except Exception as e:
        logger.error(f"Ошибка при получении деталей поста ID {post_id}: {e}")
        return f"Произошла ошибка при загрузке деталей поста: {str(e)} 🍊"


def find_user_by_username(username: str, user_info: dict) -> str:
    """
    Ищет пользователя по имени и представляет его профиль.
    """
    logger.info(f"Пользователь {user_info.get('username', 'аноним')} ищет пользователя: '{username}'")
    try:
        if CustomUser is None:
            return "Ошибка: модель пользователей не доступна."

        found_user = CustomUser.objects.get(username__iexact=username)

        # Получаем статистику пользователя
        posts_count = Post.objects.filter(author=found_user).count() if Post else 0

        # Безопасная проверка подписчиков
        subscribers_count = 0
        if Subscription and hasattr(found_user, 'subscribers'):
            try:
                subscribers_count = found_user.subscribers.count()
            except Exception as e:
                logger.warning(f"Ошибка при подсчете подписчиков: {e}")

        # Получаем последний пост для контекста
        last_post_info = "Еще не создавал постов"
        if Post:
            try:
                last_post = Post.objects.filter(author=found_user).order_by('-pub_date').first()
                if last_post:
                    last_post_info = f"Последний пост: \"{last_post.title}\""
            except Exception:
                last_post_info = "Информация о постах недоступна"

        user_bio = found_user.bio if hasattr(found_user,
                                             'bio') and found_user.bio else "Пользователь пока ничего не рассказал о себе."

        logger.info(
            f"Найден пользователь: @{found_user.username}. Постов: {posts_count}, Подписчиков: {subscribers_count}")

        return f"""👤 **Найден пользователь @{found_user.username}!**

📝 **О себе:** {user_bio}

📊 **Статистика:**
• Постов: {posts_count}
• Подписчиков: {subscribers_count}

📰 {last_post_info}

💡 Хочешь подписаться на этого автора? Перейди в его профиль!"""

    except CustomUser.DoesNotExist:
        logger.info(f"Пользователь с именем '{username}' не найден.")
        return f"К сожалению, пользователь с именем '{username}' не найден. Проверьте правильность написания имени."
    except Exception as e:
        logger.error(f"Ошибка при поиске пользователя '{username}': {e}")
        return f"Произошла ошибка при поиске пользователя: {str(e)} 🍊"


def get_user_activity(user_id: int, user_info: dict) -> str:
    """
    Получает последнюю активность пользователя без технических деталей.
    """
    requesting_user_info = user_info.get('username', 'аноним')
    logger.info(f"Пользователь {requesting_user_info} запрашивает активность пользователя с ID: {user_id}")

    try:
        if CustomUser is None:
            return "Ошибка: модель пользователей не доступна."

        target_user = CustomUser.objects.get(pk=user_id)
        target_username = target_user.username

        # Последние 3 поста пользователя
        posts_info_list = []
        if Post:
            latest_posts = Post.objects.filter(author=target_user).order_by('-pub_date')[:3]
            if latest_posts:
                for post in latest_posts:
                    try:
                        post_url = post.get_absolute_url() if hasattr(post,
                                                                      'get_absolute_url') else f"/posts/{post.id}/"
                    except Exception:
                        post_url = f"/posts/{post.id}/"
                    posts_info_list.append(f"📝 **{post.title}**\nСсылка: {post_url}")
            else:
                posts_info_list.append("📝 Недавних постов нет.")
        else:
            posts_info_list.append("📝 Информация о постах недоступна.")

        posts_activity_str = "\n\n".join(posts_info_list)

        # Последние 3 комментария пользователя
        comments_info_list = []
        if Comment:
            latest_comments = Comment.objects.filter(author=target_user).order_by('-created_at')[:3]
            if latest_comments:
                for comment in latest_comments:
                    try:
                        comment_post_url = comment.post.get_absolute_url() if comment.post and hasattr(comment.post,
                                                                                                       'get_absolute_url') else f"/posts/{comment.post.id}/" if comment.post else "URL поста недоступен"
                    except Exception:
                        comment_post_url = f"/posts/{comment.post.id}/" if comment.post else "URL поста недоступен"
                    comments_info_list.append(
                        f"💬 Прокомментировал: \"{comment.text[:60]}{'...' if len(comment.text) > 60 else ''}\"\nСсылка: {comment_post_url}")
            else:
                comments_info_list.append("💬 Недавних комментариев нет.")
        else:
            comments_info_list.append("💬 Информация о комментариях недоступна.")

        comments_activity_str = "\n\n".join(comments_info_list)

        logger.info(f"Успешно получена активность для пользователя @{target_username} (ID: {user_id}).")

        return f"""📊 **Последняя активность @{target_username}:**

**Недавние посты:**
{posts_activity_str}

**Недавние комментарии:**
{comments_activity_str}

💡 Нажми на ссылки, чтобы посмотреть посты или комментарии!"""

    except CustomUser.DoesNotExist:
        logger.warning(f"Запрошена активность для несуществующего пользователя с ID {user_id}.")
        return f"К сожалению, пользователь не найден."
    except Exception as e:
        logger.error(f"Ошибка при получении активности пользователя ID {user_id}: {e}")
        return f"Произошла ошибка при загрузке активности пользователя: {str(e)} 🍊"


def get_subscription_recommendations(user_info: dict, current_user_id: int = None) -> str:
    """Рекомендует интересных авторов для подписки с более дружелюбным форматом."""
    logger.info(f"Пользователь {user_info.get('username', 'аноним')} запрашивает рекомендации подписок")

    try:
        # Проверяем доступность моделей
        if CustomUser is None:
            logger.error("Модель CustomUser не доступна")
            return "Ошибка: модель пользователей не доступна."

        if Post is None:
            logger.error("Модель Post не доступна")
            return "Ошибка: модель постов не доступна."

        # Получаем популярных авторов
        recommended_users = CustomUser.objects.annotate(
            num_posts=Count('post')
        ).filter(
            num_posts__gt=0
        ).order_by('-num_posts')

        # Исключаем текущего пользователя
        if current_user_id:
            recommended_users = recommended_users.exclude(id=current_user_id)

            # Если модель подписок доступна, исключаем тех, на кого уже подписан
            if Subscription:
                try:
                    user = CustomUser.objects.get(id=current_user_id)
                    subscribed_ids = Subscription.objects.filter(subscriber=user).values_list('target_id', flat=True)
                    recommended_users = recommended_users.exclude(id__in=subscribed_ids)
                except Exception as e:
                    logger.warning(f"Ошибка при исключении подписок: {e}")

        recommended_users = recommended_users[:5]

        if not recommended_users:
            logger.info("Рекомендации не найдены")
            return "🍊 Пока что мало активных авторов, но скоро их станет больше! А пока создай свой первый пост!"

        authors_info = []
        for user in recommended_users:
            # Получаем последний пост для контекста
            try:
                last_post = Post.objects.filter(author=user).order_by('-pub_date').first()
                post_preview = f"Последний пост: \"{last_post.title[:30]}...\"" if last_post else "Еще нет постов"
            except Exception as e:
                logger.warning(f"Ошибка при получении последнего поста для пользователя {user.username}: {e}")
                post_preview = "Информация о постах недоступна"

            bio_info = ""
            if hasattr(user, 'bio') and user.bio:
                bio_info = f'📝 О себе: {user.bio[:80]}...'

            authors_info.append(f"""🔸 **@{user.username}** ({user.num_posts} постов)
{bio_info}
📰 {post_preview}""")

        recommendations = "\n\n".join(authors_info)
        logger.info(f"Сформированы рекомендации для {len(authors_info)} пользователей")

        return f"""🌟 **Рекомендую подписаться на этих интересных авторов:**

{recommendations}

💡 **Совет:** Подписывайся на авторов с похожими интересами, чтобы твоя лента была интересной!"""

    except Exception as e:
        logger.error(f"Ошибка при получении рекомендаций: {e}")
        return f"Не удалось загрузить рекомендации: {str(e)} 🍊"


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
    logger.info(f"Анализ профиля для пользователя ID: {user_id}")

    try:
        if CustomUser is None:
            return "Ошибка: модель пользователей не доступна."

        user = CustomUser.objects.get(id=user_id)

        # Собираем статистику
        posts_count = Post.objects.filter(author=user).count() if Post else 0
        comments_count = Comment.objects.filter(author=user).count() if Comment else 0

        # Подсчет лайков
        likes_received = 0
        if Post:
            try:
                user_posts = Post.objects.filter(author=user)
                for post in user_posts:
                    if hasattr(post, 'likes'):
                        likes_received += post.likes.count()
            except Exception as e:
                logger.warning(f"Ошибка при подсчете лайков: {e}")

        # Подписки
        subscribers_count = 0
        subscriptions_count = 0
        if Subscription:
            try:
                subscribers_count = Subscription.objects.filter(target=user).count()
                subscriptions_count = Subscription.objects.filter(subscriber=user).count()
            except Exception as e:
                logger.warning(f"Ошибка при подсчете подписок: {e}")

        # Дни на сайте
        days_on_site = 0
        if hasattr(user, 'date_joined'):
            days_on_site = (datetime.now().date() - user.date_joined.date()).days
        elif hasattr(user, 'created_at'):
            days_on_site = (datetime.now().date() - user.created_at.date()).days

        stats = {
            'posts_count': posts_count,
            'comments_count': comments_count,
            'likes_received': likes_received,
            'subscribers_count': subscribers_count,
            'subscriptions_count': subscriptions_count,
            'days_on_site': days_on_site
        }

        logger.info(f"Статистика для @{user.username}: {stats}")

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

    except CustomUser.DoesNotExist:
        logger.warning(f"Пользователь с ID {user_id} не найден для анализа профиля")
        return "Пользователь не найден."
    except Exception as e:
        logger.error(f"Ошибка анализа профиля: {e}")
        return f"Не удалось проанализировать профиль: {str(e)} 🍊"


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