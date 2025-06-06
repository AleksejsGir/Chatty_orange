import google.generativeai as genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_gemini_response(prompt: str) -> str:
    """
    Отправляет запрос к Google Gemini API и возвращает текстовый ответ.

    :param prompt: Текстовый запрос для модели Gemini.
    :return: Строка с ответом от модели или сообщение об ошибке.
    """
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        logger.error("GOOGLE_API_KEY не настроен в settings.py.")
        return "Ошибка: Ключ API для сервиса ИИ не настроен."

    genai.configure(api_key=api_key)

    # Список доступных моделей может измениться. Проверьте документацию Google.
    # На момент написания, 'gemini-pro' подходит для текстовых задач.
    model = genai.GenerativeModel('gemini-2.0-flash')

    try:
        response = model.generate_content(prompt)
        # Убедимся, что у ответа есть текстовая часть.
        # Структура ответа может немного отличаться в зависимости от версии API и типа контента.
        if response.parts:
            return "".join(part.text for part in response.parts if hasattr(part, 'text'))
        elif hasattr(response, 'text') and response.text:
            return response.text
        else:
            # Попытка извлечь текст, если он есть в другом месте или обработать ошибку
            # Это может потребовать более детального изучения структуры ответа Gemini
            # для случаев, когда parts пустые, но ответ все же есть.
            logger.warning(f"Ответ от Gemini не содержит ожидаемой текстовой части. Ответ: {response}")
            # Проверяем наличие кандидатов и текста в них
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                return "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
            return "ИИ не смог сгенерировать ответ в ожидаемом формате."

    except Exception as e:
        logger.error(f"Ошибка при взаимодействии с Gemini API: {e}")
        # В случае ошибки можно вернуть более общее сообщение пользователю
        # или специфичное, если это безопасно и полезно для отладки.
        return f"Произошла ошибка при обращении к сервису ИИ. Подробности: {str(e)}"


# TODO: Реализовать специфичные функции для каждой задачи ИИ, как указано в плане.
# Например:
def get_interactive_tour_step(step_number: int, user_info: dict) -> str:
    # Определяем тему шага на основе его номера.
    # Это можно вынести в отдельную функцию или конфигурацию, если шагов будет много.
    tour_step_topics = {
        1: "Знакомство с Chatty Orange",
        2: "Создание первого поста",
        3: "Лента и взаимодействие (лайки, комментарии)",
        4: "Поиск друзей и подписки",
        5: "Настройки профиля и приватность"
    }
    tour_step_topic = tour_step_topics.get(step_number, "Обзор дополнительных функций")

    prompt = f"Это шаг {step_number} интерактивного онлайн-тура по социальной сети Chatty Orange для пользователя {user_info.get('username', 'Аноним')}. Тема шага: {tour_step_topic}. Расскажи кратко и дружелюбно об этой теме. Например: Шаг 1 (Тема: Знакомство с Chatty Orange) - Приветствие и краткий обзор основных возможностей. Шаг 2 (Тема: Создание первого поста) - Как создать свой первый пост, какие есть опции. Шаг 3 (Тема: Лента и взаимодействие) - Как работает лента, лайки, комментарии."
    return get_gemini_response(prompt)


def get_post_creation_suggestion(current_text: str, user_info: dict) -> str:
    prompt = f"Пользователь {user_info.get('username', 'Аноним')} на сайте Chatty Orange пытается создать свой первый пост. Его текущий текст: '{current_text}'. Помоги ему: предложи 3-4 идеи для первого поста на общие темы (например, приветствие, хобби, мысли о сегодняшнем дне) или, если текст уже есть, предложи как его можно улучшить или продолжить. Ответ должен быть в виде прямого совета или предложения."
    return get_gemini_response(prompt)


#
# ... и так далее для других функций.


def get_faq_answer(question: str, user_info: dict) -> str:
    prompt = f"Пользователь {user_info.get('username', 'аноним')} задает вопрос о сайте Chatty Orange: '{question}'. Ответь на этот вопрос подробно и дружелюбно. Если вопрос не по теме сайта Chatty Orange или его функционала, вежливо укажи на это. При необходимости, можешь предположить, что Chatty Orange - это социальная сеть со стандартным набором функций (посты, лайки, комментарии, подписки, профили пользователей)."
    return get_gemini_response(prompt)


def get_feature_explanation(feature_query: str, user_info: dict) -> str:
    prompt = f"Пользователь {user_info.get('username', 'аноним')} спрашивает о функции '{feature_query}' на сайте Chatty Orange. Подробно объясни, что это за функция, как ею пользоваться, и какие преимущества она дает. Если точное название функции неизвестно, но понятен контекст из запроса '{feature_query}', объясни наиболее подходящую по смыслу функцию. Chatty Orange - это социальная сеть."
    return get_gemini_response(prompt)


def get_subscription_recommendations(user_info: dict, current_user_id: int = None) -> str:
    from django.db.models import Count
    from users.models import CustomUser
    # Модель Subscription не используется напрямую для подсчета, Count('subscribers') относится к related_name
    # from subscriptions.models import Subscription

    try:
        recommended_users = CustomUser.objects.annotate(
            num_subscribers=Count('subscribers')  # 'subscribers' - это related_name от Subscription.target
        ).order_by('-num_subscribers', '-created_at')  # Добавим сортировку по дате создания для стабильности

        if current_user_id:
            recommended_users = recommended_users.exclude(id=current_user_id)

        # Также исключим пользователей, на которых текущий пользователь уже подписан, если current_user_id есть
        if current_user_id:
            try:
                user = CustomUser.objects.get(id=current_user_id)
                subscribed_to_ids = user.subscriptions.values_list('target_id', flat=True)
                recommended_users = recommended_users.exclude(id__in=subscribed_to_ids)
            except CustomUser.DoesNotExist:
                logger.warning(
                    f"get_subscription_recommendations: User with id {current_user_id} not found, cannot exclude subscribed users.")

        recommended_users = recommended_users[:5]  # Возьмем топ-5 из оставшихся

        if not recommended_users:
            return "Пока некого рекомендовать, но скоро здесь появятся интересные авторы! Заглядывайте позже."

        authors_details_list = []
        for r_user in recommended_users:
            detail = f"- @{r_user.username} ({r_user.num_subscribers} подписчиков)."
            if r_user.bio:
                detail += f" Bio: {r_user.bio_short}"  # Предполагаем, что есть bio_short или используем bio
            authors_details_list.append(detail)

        authors_details = "\n".join(authors_details_list)

        prompt = f"""Пользователь {user_info.get('username', 'Аноним')} ищет на кого подписаться в социальной сети Chatty Orange.
Вот несколько интересных авторов:
{authors_details}

Представь этих авторов кратко и привлекательно, по одному предложению на каждого.
Укажи их имена (@username) и, возможно, чем они могут быть интересны, основываясь на их описании (bio) или количестве подписчиков.
Ответ должен быть в виде списка (маркированного или нумерованного) или нескольких коротких абзацев, удобных для чтения.
Например:
- @ИванИванов (150 подписчиков) - делится яркими фотографиями из путешествий!
- @ЕленаПетрова (120 подписчиков) - пишет интересные заметки о книгах."""

        return get_gemini_response(prompt)

    except Exception as e:
        logger.error(f"Ошибка при получении рекомендаций подписок: {e}")
        return "Не удалось получить рекомендации подписок из-за внутренней ошибки. Попробуйте позже."


def check_post_content(post_text: str, user_info: dict) -> str:
    """
    Проверяет текст поста на соответствие правилам сайта с помощью Gemini.
    """
    if not post_text or not post_text.strip():
        return "Текст поста не может быть пустым для проверки."

    # Правила сайта Chatty Orange для ИИ
    site_rules = """1. Запрещены оскорбления, угрозы и проявление агрессии.
2. Запрещен контент для взрослых (18+), насильственный или шокирующий контент.
3. Запрещен спам, несогласованная реклама и мошенничество.
4. Запрещено разжигание ненависти по расовому, религиозному, национальному, половому или любому другому признаку.
5. Запрещено выдавать себя за другого человека (если это очевидно из текста).
6. Контент должен быть оригинальным. При использовании цитат или заимствованного контента указывайте источник или автора. (ИИ может проверить это только косвенно, по общему смыслу).
7. Язык общения на сайте - преимущественно русский. Пожалуйста, укажи, если текст не на русском. Это мягкое правило, просто отметь факт.
8. Запрещено обсуждение или пропаганда незаконной деятельности."""

    prompt = f"""Пользователь {user_info.get('username', 'Аноним')} на сайте Chatty Orange написал следующий текст для своего поста:
---
{post_text}
---

Пожалуйста, внимательно проверь этот текст на соответствие следующим правилам сайта Chatty Orange:
{site_rules}

Твоя задача - оценить текст поста.
- Если текст полностью соответствует всем правилам, твой ответ должен быть: "Текст выглядит хорошо и соответствует правилам."
- Если есть потенциальные нарушения или текст не соответствует какому-либо из правил, четко укажи, какое именно правило (или правила) может быть нарушено и почему. Будь конкретным, но вежливым в своих формулировках. Приведи примеры из текста, если это помогает пояснить проблему.
- Если текст написан не на русском языке, укажи это как мягкое наблюдение (например: "Текст написан не на русском языке. Основной язык общения на сайте - русский."). Это не строгое нарушение, а рекомендация.
- Если нарушений несколько, перечисли их все.

Примеры ответов при наличии нарушений:
- "Обнаружено возможное нарушение правила 1 (Оскорбления): фраза 'ты полный идиот' может быть воспринята как прямое оскорбление."
- "Потенциальное нарушение правила 3 (Спам): текст содержит множество ссылок и призывов перейти на сторонний ресурс, что похоже на спам."
- "Текст, возможно, нарушает правило 2 (Контент для взрослых), так как содержит детальные описания сцен насилия."
- "Текст написан на английском языке. Напоминаем, что основной язык общения на Chatty Orange - русский. Тем не менее, по содержанию других нарушений не найдено."

Твой ответ должен быть четким, конструктивным и понятным для пользователя, который хочет опубликовать пост."""

    try:
        return get_gemini_response(prompt)
    except Exception as e:
        logger.error(f"Ошибка при проверке контента поста: {e}")
        return "Не удалось выполнить проверку поста из-за внутренней ошибки. Попробуйте позже."