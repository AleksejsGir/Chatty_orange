import json
import logging
import re
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .ai_services import (
    get_gemini_response,
    get_faq_answer,
    get_feature_explanation,
    get_interactive_tour_step,
    get_post_creation_suggestion,
    get_subscription_recommendations,
    check_post_content,
    analyze_profile_stats,
    generate_post_ideas,
    analyze_sentiment,
    find_post_by_keyword,
    get_post_details,
    find_user_by_username,
    get_user_activity
)

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class ChatWithAIView(View):
    """Основной view для взаимодействия с ИИ-помощником."""

    def post(self, request, *args, **kwargs):
        try:
            # Загружаем данные из запроса
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            action_type = data.get('action_type')
            user_input = data.get('user_input', '')
            user_info = data.get('user_info', {})

            # Добавляем информацию о текущем пользователе
            if request.user.is_authenticated:
                user_info.update({
                    'user_id': request.user.id,
                    'username': request.user.username,
                    'is_authenticated': True
                })
            else:
                user_info.update({
                    'user_id': None,
                    'username': user_info.get('username', 'Гость'),
                    'is_authenticated': False
                })

            # Логируем запрос для статистики
            logger.info(
                f"AI request: action={action_type}, user={user_info.get('username')}, input='{user_input[:50]}...'")

            # Обработка различных типов действий
            try:
                if action_type == 'faq':
                    if not user_input:
                        return JsonResponse({'error': 'Введите ваш вопрос'}, status=400)
                    ai_response = get_faq_answer(question=user_input, user_info=user_info)

                elif action_type == 'feature_explanation':
                    if not user_input:
                        return JsonResponse({'error': 'Укажите функцию для объяснения'}, status=400)
                    ai_response = get_feature_explanation(feature_query=user_input, user_info=user_info)

                elif action_type == 'general_chat':
                    if not user_input:
                        ai_response = f"Привет, {user_info.get('username')}! 👋 Я твой Апельсиновый Помощник! Чем могу помочь?"
                    else:
                        # Используем обработку естественного языка
                        ai_response = self.handle_natural_language_query(user_input, user_info)

                elif action_type == 'interactive_tour_step':
                    step_number = data.get('step_number')
                    if step_number is None:
                        return JsonResponse({'error': 'Не указан номер шага'}, status=400)
                    try:
                        step_number = int(step_number)
                    except ValueError:
                        return JsonResponse({'error': 'Номер шага должен быть числом'}, status=400)
                    ai_response = get_interactive_tour_step(step_number=step_number, user_info=user_info)

                elif action_type == 'post_creation_suggestion':
                    current_text = data.get('current_text', '')
                    ai_response = get_post_creation_suggestion(current_text=current_text, user_info=user_info)

                elif action_type == 'subscription_recommendations':
                    current_user_id = user_info.get('user_id') if user_info.get('is_authenticated') else None
                    ai_response = get_subscription_recommendations(user_info=user_info, current_user_id=current_user_id)

                elif action_type == 'check_post_content':
                    if not user_input:
                        return JsonResponse({'error': 'Введите текст для проверки'}, status=400)
                    ai_response = check_post_content(post_text=user_input, user_info=user_info)

                elif action_type == 'analyze_profile':
                    if not user_info.get('is_authenticated'):
                        ai_response = "🔒 Эта функция доступна только авторизованным пользователям!"
                    else:
                        ai_response = analyze_profile_stats(user_id=user_info.get('user_id'))

                elif action_type == 'generate_post_ideas':
                    tags = data.get('tags', [])
                    ai_response = generate_post_ideas(user_info=user_info, tags=tags)

                elif action_type == 'analyze_sentiment':
                    if not user_input:
                        return JsonResponse({'error': 'Введите текст для анализа'}, status=400)
                    ai_response = analyze_sentiment(text=user_input)

                elif action_type == 'find_post_by_keyword':
                    # Извлекаем ключевое слово из user_input
                    keyword = self.extract_keyword_for_posts(user_input)
                    if not keyword:
                        return JsonResponse({'error': 'Не удалось извлечь ключевое слово для поиска'}, status=400)
                    logger.info(f"Extracted keyword for post search: '{keyword}'")
                    ai_response = find_post_by_keyword(keyword=keyword, user_info=user_info)

                elif action_type == 'get_post_details':
                    post_id = data.get('post_id')
                    if not post_id:
                        # Попробуем извлечь ID из user_input
                        numbers = re.findall(r'\d+', user_input)
                        if numbers:
                            post_id = numbers[0]
                        else:
                            return JsonResponse({'error': 'Не указан ID поста'}, status=400)
                    try:
                        post_id = int(post_id)
                    except ValueError:
                        return JsonResponse({'error': 'ID поста должен быть числом'}, status=400)
                    ai_response = get_post_details(post_id=post_id, user_info=user_info)

                elif action_type == 'find_user_by_username':
                    # Извлекаем имя пользователя из user_input
                    username = self.extract_username(user_input)
                    if not username:
                        return JsonResponse({'error': 'Не удалось извлечь имя пользователя'}, status=400)
                    logger.info(f"Extracted username: '{username}'")
                    ai_response = find_user_by_username(username=username, user_info=user_info)

                elif action_type == 'get_user_activity':
                    user_id_target = data.get('user_id_target')
                    if not user_id_target:
                        # Попробуем извлечь ID из user_input
                        numbers = re.findall(r'\d+', user_input)
                        if numbers:
                            user_id_target = numbers[0]
                        else:
                            return JsonResponse({'error': 'Не указан ID целевого пользователя'}, status=400)
                    try:
                        user_id_target = int(user_id_target)
                    except ValueError:
                        return JsonResponse({'error': 'ID целевого пользователя должен быть числом'}, status=400)
                    ai_response = get_user_activity(user_id=user_id_target, user_info=user_info)

                else:
                    # Обработка естественного языка для неизвестных типов
                    ai_response = self.handle_natural_language_query(user_input, user_info)

            except Exception as action_error:
                logger.error(f"Ошибка при выполнении действия {action_type}: {action_error}")
                ai_response = f"Произошла ошибка при выполнении запроса: {str(action_error)} 🍊"

            # Сохраняем статистику использования (опционально)
            self.save_usage_stats(action_type, user_info)

            logger.info(f"AI response length: {len(ai_response)} chars")

            return JsonResponse({
                'response': ai_response,
                'timestamp': timezone.now().isoformat()
            })

        except json.JSONDecodeError:
            logger.error("JSON decode error in ChatWithAIView")
            return JsonResponse({'error': 'Неверный формат данных'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in ChatWithAIView: {e}")
            return JsonResponse({'error': 'Внутренняя ошибка сервера'}, status=500)

    def extract_username(self, user_input: str) -> str:
        """Извлекает имя пользователя из текста."""
        lower_input = user_input.lower().strip()

        # Паттерны для извлечения имени
        patterns_to_try = [
            # "найди пользователя Orange"
            r'(?:найди|найти|ищи|искать|покажи)\s+(?:пользователя|юзера)\s+(\w+)',
            # "пользователь Orange"
            r'пользователь\s+(\w+)',
            # "профиль Orange"
            r'профиль\s+(\w+)',
            # "@Orange"
            r'@(\w+)',
            # "в профиле Orange"
            r'в\s+профиле\s+(\w+)',
            # "кто такой Orange"
            r'кто\s+такой\s+(\w+)',
        ]

        for pattern in patterns_to_try:
            match = re.search(pattern, lower_input)
            if match:
                return match.group(1)

        # Если не нашли через регулярки, пробуем простой подход
        words = user_input.split()
        for i, word in enumerate(words):
            if word.lower() in ['пользователя', 'юзера', 'пользователь', 'профиль'] and i + 1 < len(words):
                return words[i + 1].replace('@', '').strip()

        return None

    def extract_keyword_for_posts(self, user_input: str) -> str:
        """Извлекает ключевое слово для поиска постов."""
        lower_input = user_input.lower().strip()

        # Сначала пробуем найти текст в скобках или кавычках
        bracket_match = re.search(r'[(\[]([^)\]]+)[)\]]', user_input)
        if bracket_match:
            keyword = bracket_match.group(1).strip()
            logger.info(f"Found keyword in brackets: '{keyword}'")
            return keyword

        # Ищем ключевое слово после предлогов
        keyword_patterns = [
            r'про\s+(.+)',
            r'о\s+(.+)',
            r'об\s+(.+)',
            r'по\s+теме\s+(.+)',
            r'на\s+тему\s+(.+)',
            # Для "найди пост XXXX"
            r'(?:найди|найти|ищи|искать)\s+(?:пост|посты|стать|статьи)\s+(.+)',
            # Просто последние слова после "пост"
            r'пост\s+(.+)',
            r'посты\s+(.+)',
            r'статьи?\s+(.+)'
        ]

        for pattern in keyword_patterns:
            match = re.search(pattern, lower_input)
            if match:
                keyword = match.group(1).strip()
                # Убираем знаки препинания в конце
                keyword = re.sub(r'[?!.,:;]+$', '', keyword)
                return keyword

        return None

    def handle_natural_language_query(self, user_input: str, user_info: dict) -> str:
        """Обрабатывает запросы на естественном языке."""
        lower_input = user_input.lower().strip()

        logger.info(f"Processing natural language query: '{user_input}' from {user_info.get('username', 'anonymous')}")

        # ===============================
        # КРИТИЧЕСКИ ВАЖНО: СНАЧАЛА ПРОВЕРЯЕМ ПОИСК ПОСТОВ ПОЛЬЗОВАТЕЛЯ
        # ===============================

        # Убираем markdown форматирование в самом начале
        clean_input = re.sub(r'\*\*(.*?)\*\*', r'\1', user_input)
        clean_lower = clean_input.lower().strip()

        # СУПЕР-АГРЕССИВНАЯ проверка на поиск постов пользователя
        user_posts_indicators = [
            'статьи у', 'посты у', 'какие статьи у', 'какие посты у',
            'статьи пользователя', 'посты пользователя',
            'статьи от', 'посты от',
            'что писал', 'что писала',
            'статьи у пользователя', 'посты у пользователя'
        ]

        # Паттерны для извлечения имени (БЕЗ **форматирования**)
        username_patterns = [
            r'(?:статьи|посты)\s+у\s+([A-Za-z0-9_-]+)',
            r'(?:статьи|посты)\s+пользователя\s+([A-Za-z0-9_-]+)',
            r'что\s+(?:писал|писала)\s+([A-Za-z0-9_-]+)',
            r'какие\s+(?:статьи|посты)\s+у\s+([A-Za-z0-9_-]+)',
            r'(?:статьи|посты)\s+от\s+([A-Za-z0-9_-]+)',
            r'(?:статьи|посты)\s+у\s+пользователя\s+([A-Za-z0-9_-]+)',
            # Для "какие статьи Orange" (без предлогов)
            r'какие\s+(?:статьи|посты)\s+([A-Za-z0-9_-]+)(?:\s|$|\?)',
        ]

        # ПРОВЕРЯЕМ: содержит ли запрос индикаторы поиска постов пользователя?
        contains_user_posts_indicator = any(indicator in clean_lower for indicator in user_posts_indicators)

        # ДОПОЛНИТЕЛЬНАЯ проверка для "какие статьи Username"
        if not contains_user_posts_indicator:
            if re.search(r'какие\s+(?:статьи|посты)\s+[A-Za-z0-9_-]+', clean_lower):
                contains_user_posts_indicator = True

        if contains_user_posts_indicator:
            logger.info("DETECTED: User posts query - prioritizing user search")

            # Пытаемся извлечь имя пользователя
            username = None
            for pattern in username_patterns:
                match = re.search(pattern, clean_input, re.IGNORECASE)
                if match:
                    username = match.group(1)
                    logger.info(f"Extracted username: '{username}' via pattern: {pattern}")
                    break

            # Если не нашли через паттерны, пробуем другой способ
            if not username:
                words = clean_input.split()
                for i, word in enumerate(words):
                    if word.lower() in ['статьи', 'посты']:
                        # Ищем следующее слово после статьи/посты, пропуская служебные
                        for j in range(i + 1, len(words)):
                            next_word = words[j].strip('?!.,')
                            if (next_word.lower() not in ['у', 'от', 'пользователя', 'про', 'о', 'об', 'по', 'с'] and
                                    len(next_word) > 1 and re.match(r'^[A-Za-z0-9_-]+$', next_word)):
                                username = next_word
                                logger.info(f"Extracted username via fallback: '{username}'")
                                break
                        if username:
                            break

            # Если найден пользователь - ищем его посты
            if username:
                try:
                    from posts.models import Post
                    from users.models import CustomUser

                    user = CustomUser.objects.get(username__iexact=username)
                    user_posts = Post.objects.filter(author=user).order_by('-pub_date')[:10]

                    if user_posts.exists():
                        posts_info = []
                        for post in user_posts:
                            try:
                                post_url = post.get_absolute_url() if hasattr(post,
                                                                              'get_absolute_url') else f"/posts/{post.id}/"
                            except:
                                post_url = f"/posts/{post.id}/"
                            posts_info.append(f"• **{post.title}** (ID: {post.id})\n  Ссылка: {post_url}")

                        posts_list = "\n\n".join(posts_info)
                        return f"📝 **Посты пользователя @{username}:**\n\n{posts_list}\n\n💡 Чтобы узнать больше о конкретном посте, напиши: 'Расскажи о посте [ID]'"
                    else:
                        return f"📝 У пользователя @{username} пока нет опубликованных постов."

                except CustomUser.DoesNotExist:
                    return f"❌ Пользователь '{username}' не найден."
                except Exception as e:
                    logger.error(f"Error searching posts by user {username}: {e}")
                    return f"❌ Ошибка при поиске постов пользователя {username}: {e}"
            else:
                # Если не удалось извлечь имя пользователя из запроса с индикаторами
                return """🔍 Не удалось определить пользователя. Попробуйте:

    **Примеры правильных команд:**
    • 'Какие статьи у Orange?'
    • 'Посты пользователя Alek'  
    • 'Что писал Orange?'
    • 'Статьи от Orange'"""

        # ===============================
        # ТОЛЬКО ПОСЛЕ проверки пользователей - общий поиск постов
        # ===============================

        general_post_search_patterns = [
            'найди пост', 'найти пост', 'ищи пост', 'искать пост',
            'найди стать', 'найти стать', 'покажи пост',
            'найди посты про', 'найти посты про', 'ищи посты про'
        ]

        if any(pattern in lower_input for pattern in general_post_search_patterns):
            logger.info("Detected general post search query")
            keyword = self.extract_keyword_for_posts(user_input)
            if keyword:
                logger.info(f"Searching posts with keyword: '{keyword}'")
                return find_post_by_keyword(keyword, user_info)
            else:
                return """🔍 Укажите тему для поиска. Примеры:

    **Поиск по теме:**
    • 'Найди посты про путешествия'
    • 'Найди пост (QLED телевизоры)'

    **Посты пользователя:**
    • 'Какие статьи у Orange?'
    • 'Посты пользователя Alek'
    • 'Что писал Orange?'"""

        # === ПОИСК ПОЛЬЗОВАТЕЛЕЙ ===
        user_search_patterns = [
            'найди пользователя', 'найти пользователя', 'ищи пользователя',
            'найди юзера', 'профиль', 'кто такой'
        ]

        if any(pattern in lower_input for pattern in user_search_patterns):
            username = self.extract_username(user_input)
            if username:
                logger.info(f"Searching user: '{username}'")
                return find_user_by_username(username, user_info)
            else:
                return "❌ Не удалось извлечь имя пользователя. Попробуйте: 'Найди пользователя [имя]'"

        # === ДЕТАЛИ ПОСТА ===
        post_detail_patterns = [
            'расскажи о посте', 'пост номер', 'пост id', 'детали поста',
            'покажи пост', 'что в посте', 'открой пост'
        ]

        if any(pattern in lower_input for pattern in post_detail_patterns):
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                try:
                    post_id = int(numbers[0])
                    logger.info(f"Getting post details for ID: {post_id}")
                    return get_post_details(post_id, user_info)
                except ValueError:
                    pass

            return "🔢 Укажите ID поста. Например: 'Расскажи о посте 5' или 'Покажи пост 123'"

        # === АКТИВНОСТЬ ПОЛЬЗОВАТЕЛЯ ===
        activity_patterns = [
            'что нового у', 'активность пользователя', 'что делает',
            'последние посты', 'недавняя активность'
        ]

        if any(pattern in lower_input for pattern in activity_patterns):
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                try:
                    user_id = int(numbers[0])
                    logger.info(f"Getting user activity for ID: {user_id}")
                    return get_user_activity(user_id, user_info)
                except ValueError:
                    pass

            username_patterns = [
                r'что\s+нового\s+у\s+(\w+)',
                r'активность\s+пользователя\s+(\w+)',
                r'что\s+делает\s+(\w+)'
            ]

            for pattern in username_patterns:
                match = re.search(pattern, lower_input)
                if match:
                    username = match.group(1)
                    try:
                        from users.models import CustomUser
                        user = CustomUser.objects.get(username__iexact=username)
                        return get_user_activity(user.id, user_info)
                    except CustomUser.DoesNotExist:
                        return f"❌ Пользователь '{username}' не найден."
                    except Exception as e:
                        logger.error(f"Error getting user activity: {e}")
                        return f"❌ Ошибка: {e}"

            return "👤 Укажите пользователя. Например: 'Что нового у пользователя 1?' или 'Активность Orange'"

        # === РЕКОМЕНДАЦИИ ===
        recommendation_patterns = [
            'кого почитать', 'рекомендации', 'посоветуй авторов',
            'интересные авторы', 'на кого подписаться'
        ]

        if any(pattern in lower_input for pattern in recommendation_patterns):
            logger.info("Getting subscription recommendations")
            current_user_id = user_info.get('user_id') if user_info.get('is_authenticated') else None
            return get_subscription_recommendations(user_info, current_user_id)

        # === ОБЩИЙ ЧАТ ===
        logger.info(f"Processing as general chat: '{user_input}'")

        help_suggestions = []

        if 'пользователь' in lower_input or 'юзер' in lower_input:
            help_suggestions.append("💡 Для поиска пользователя: 'Найди пользователя [имя]'")

        if 'пост' in lower_input or 'стать' in lower_input:
            help_suggestions.append("💡 Для поиска постов: 'Найди посты про [тема]'")
            help_suggestions.append("💡 Для деталей поста: 'Расскажи о посте [ID]'")
            help_suggestions.append("💡 Для поиска в скобках: 'Найди пост (ключевое слово)'")

        if 'рекоменд' in lower_input or 'совет' in lower_input:
            help_suggestions.append("💡 Для рекомендаций: 'Кого почитать?'")

        prompt = f"""Пользователь {user_info.get('username')} пишет: '{user_input}'
        Контекст: социальная сеть Chatty Orange.

        Ответь дружелюбно и полезно, используй эмодзи. 

        {f'Добавь эти подсказки в конце ответа: {chr(10).join(help_suggestions)}' if help_suggestions else ''}

        Если пользователь ищет что-то конкретное, предложи правильный формат команды:
        - "Найди пользователя [имя]" - для поиска людей
        - "Найди посты про [тема]" или "Найди пост (тема)" - для поиска постов
        - "Расскажи о посте [ID]" - для деталей поста
        - "Кого почитать?" - для рекомендаций
        """

        return get_gemini_response(prompt)

    def get(self, request, *args, **kwargs):
        """Информация об API."""
        return JsonResponse({
            'message': 'Chatty Orange AI Assistant API',
            'version': '2.1',
            'status': 'active',
            'endpoints': {
                'faq': 'Ответы на вопросы о сайте',
                'feature_explanation': 'Объяснение функций',
                'general_chat': 'Общий чат',
                'interactive_tour_step': 'Интерактивный тур',
                'post_creation_suggestion': 'Помощь в создании постов',
                'subscription_recommendations': 'Рекомендации подписок',
                'check_post_content': 'Проверка контента',
                'analyze_profile': 'Анализ профиля',
                'generate_post_ideas': 'Генерация идей',
                'analyze_sentiment': 'Анализ настроения',
                'find_post_by_keyword': 'Поиск постов по ключевому слову',
                'get_post_details': 'Получение деталей поста по ID',
                'find_user_by_username': 'Поиск пользователя по имени',
                'get_user_activity': 'Получение активности пользователя по ID'
            },
            'natural_language_examples': [
                'Найди пользователя Orange',
                'Найди посты про путешествия',
                'Найди пост (QLED телевизоры)',
                'Расскажи о посте 5',
                'Что нового у пользователя 1?',
                'Кого почитать?'
            ]
        })

    def save_usage_stats(self, action_type, user_info):
        """Сохраняет статистику использования ИИ (для будущей аналитики)."""
        try:
            # Здесь можно сохранять в БД или отправлять в аналитику
            logger.info(f"Usage stat: {action_type} by {user_info.get('username', 'anonymous')}")
        except Exception as e:
            logger.warning(f"Ошибка при сохранении статистики: {e}")