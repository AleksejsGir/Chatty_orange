import json
import logging

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt # Используем csrf_exempt для упрощения на начальном этапе.
                                                     # В продакшене лучше настроить CSRF правильно для AJAX.

from .ai_services import get_gemini_response, get_faq_answer, get_feature_explanation, get_interactive_tour_step, get_post_creation_suggestion, get_subscription_recommendations, check_post_content # Импортируем наш сервис

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
            user_input = data.get('user_input', '') # Текст от пользователя (для faq, feature_explanation, general_chat)
            user_info = data.get('user_info', {}) # Дополнительная информация о пользователе, если передается

            # Параметры, специфичные для новых action_types
            step_number = data.get('step_number') # Для interactive_tour_step
            current_text = data.get('current_text', '') # Для post_creation_suggestion

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
            elif action_type == 'interactive_tour_step':
                if step_number is None: # Проверяем наличие step_number
                    return JsonResponse({'error': 'Для action_type "interactive_tour_step" нужен параметр "step_number".'}, status=400)
                try:
                    step_number = int(step_number) # Убедимся, что это число
                except ValueError:
                    return JsonResponse({'error': 'Параметр "step_number" должен быть целым числом.'}, status=400)
                ai_response = get_interactive_tour_step(step_number=step_number, user_info=user_info)
            elif action_type == 'post_creation_suggestion':
                # current_text может быть пустым, это нормально
                ai_response = get_post_creation_suggestion(current_text=current_text, user_info=user_info)
            elif action_type == 'subscription_recommendations':
                current_user_id = request.user.id if request.user.is_authenticated else None
                ai_response = get_subscription_recommendations(user_info=user_info, current_user_id=current_user_id)
            elif action_type == 'check_post_content':
                post_text = data.get('user_input', '') # Используем user_input для текста поста
                if not post_text.strip():
                    return JsonResponse({'error': 'Для action_type "check_post_content" нужен непустой параметр "user_input" (текст поста).'}, status=400)
                ai_response = check_post_content(post_text=post_text, user_info=user_info)
            else:
                # Если action_type не распознан, можно использовать general_chat или вернуть ошибку
                logger.warning(f"Неизвестный action_type: {action_type}. Используется fallback.")
                # Формируем более общий промпт для нераспознанных типов, чтобы ИИ мог попытаться помочь
                # Этот fallback должен быть достаточно общим.
                # Убираем user_input, current_text, step_number из этого общего fallback,
                # так как они могут быть нерелевантны или даже сбивать с толку ИИ, если action_type действительно неизвестен.
                # Вместо этого, можно просто сказать, что тип действия не распознан.
                # Либо, если хотим передавать все, что есть, то предыдущий вариант был ок.
                # Сейчас сделаем его более простым:
                logger.info(f"Fallback: action_type='{action_type}', user_input='{user_input}', current_text='{current_text}', step_number='{step_number}'")
                prompt = (f"Пользователь {user_info.get('username', 'Аноним')} отправил запрос с неизвестным/неподдерживаемым типом действия '{action_type}'. "
                            f"Текст пользователя (если есть): '{user_input}'. "
                            "Сообщи пользователю, что такой тип действия не поддерживается или попробуй ответить по контексту, если это имеет смысл для Chatty Orange.")
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
