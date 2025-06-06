import json
import logging

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt # Используем csrf_exempt для упрощения на начальном этапе.
                                                     # В продакшене лучше настроить CSRF правильно для AJAX.

from .ai_services import get_gemini_response, get_faq_answer, get_feature_explanation # Импортируем наш сервис

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch') # Отключаем CSRF-защиту для этого View.
                                                # ВАЖНО: Для продакшена рассмотрите более безопасные подходы.
class ChatWithAIView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Пытаемся загрузить данные из JSON-тела запроса
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                # Если это обычный POST-запрос (например, из формы)
                data = request.POST

            action_type = data.get('action_type')
            user_input = data.get('user_input', '') # Текст от пользователя
            user_info = data.get('user_info', {}) # Дополнительная информация о пользователе, если передается

            if not action_type:
                return JsonResponse({'error': 'Параметр action_type не указан'}, status=400)

            ai_response = ""
            if action_type == 'faq':
                if not user_input:
                    return JsonResponse({'error': 'Для action_type "faq" нужен параметр "user_input" (вопрос).'}, status=400)
                ai_response = get_faq_answer(question=user_input, user_info=user_info)
            elif action_type == 'feature_explanation':
                if not user_input:
                    return JsonResponse({'error': 'Для action_type "feature_explanation" нужен параметр "user_input" (название функции/запрос).'}, status=400)
                ai_response = get_feature_explanation(feature_query=user_input, user_info=user_info)
            elif action_type == 'general_chat':
                # Логика для general_chat, как была раньше или немного доработанная
                if not user_input:
                    prompt = f"Пользователь {user_info.get('username', 'аноним')} открыл чат с ИИ-помощником на сайте Chatty Orange, но ничего не написал. Поприветствуй его и предложи помощь."
                else:
                    prompt = f"Пользователь {user_info.get('username', 'аноним')} (контекст: {json.dumps(user_info, ensure_ascii=False)}) пишет в общем чате ИИ-помощника на сайте Chatty Orange: '{user_input}'. Поддержи разговор или ответь на его вопрос."
                ai_response = get_gemini_response(prompt)
            else:
                # Если action_type не распознан, можно использовать general_chat или вернуть ошибку
                logger.warning(f"Неизвестный action_type: {action_type}. Используется general_chat.")
                prompt = f"Пользователь {user_info.get('username', 'аноним')} (контекст: {json.dumps(user_info, ensure_ascii=False)}) отправил запрос с типом '{action_type}' и текстом: '{user_input}'. Постарайся ответить на это как можно лучше в контексте сайта Chatty Orange."
                ai_response = get_gemini_response(prompt)
                # Либо: return JsonResponse({'error': f'Неизвестный action_type: {action_type}'}, status=400)

            return JsonResponse({'response': ai_response})

        except json.JSONDecodeError:
            logger.error("Ошибка декодирования JSON в ChatWithAIView")
            return JsonResponse({'error': 'Неверный формат JSON в теле запроса'}, status=400)
        except Exception as e:
            logger.error(f"Неожиданная ошибка в ChatWithAIView: {e}")
            return JsonResponse({'error': f'Внутренняя ошибка сервера: {str(e)}'}, status=500)

    def get(self, request, *args, **kwargs):
        # Можно добавить простой ответ для GET-запросов, если это необходимо для отладки
        return JsonResponse({'message': 'Это эндпоинт для AI ассистента. Используйте POST-запросы.'})
