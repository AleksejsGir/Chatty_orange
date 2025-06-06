import json
import logging
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
    analyze_sentiment
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
            logger.info(f"AI request: action={action_type}, user={user_info.get('username')}")

            # Обработка различных типов действий
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
                    prompt = f"""Пользователь {user_info.get('username')} пишет: '{user_input}'
                    Контекст: социальная сеть Chatty Orange.
                    Ответь дружелюбно и полезно, используй эмодзи."""
                    ai_response = get_gemini_response(prompt)

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
                current_user_id = user_info.get('user_id')
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

            else:
                # Неизвестный тип действия
                logger.warning(f"Unknown action_type: {action_type}")
                ai_response = "🤔 Я пока не умею это делать, но постоянно учусь! Попробуй другую функцию."

            # Сохраняем статистику использования (опционально)
            self.save_usage_stats(action_type, user_info)

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

    def get(self, request, *args, **kwargs):
        """Информация об API."""
        return JsonResponse({
            'message': 'Chatty Orange AI Assistant API',
            'version': '2.0',
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
                'analyze_sentiment': 'Анализ настроения'
            }
        })

    def save_usage_stats(self, action_type, user_info):
        """Сохраняет статистику использования ИИ (для будущей аналитики)."""
        # Здесь можно сохранять в БД или отправлять в аналитику
        pass