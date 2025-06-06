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
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

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
    prompt = f"Это шаг {step_number} интерактивного тура для пользователя {user_info.get('username', 'аноним')}. Что мне показать/рассказать?"
    return get_gemini_response(prompt)

def get_post_creation_suggestion(current_text: str, user_info: dict) -> str:
    prompt = f"Пользователь {user_info.get('username', 'аноним')} пишет пост. Текущий текст: '{current_text}'. Предложи идею для продолжения или улучшения."
    return get_gemini_response(prompt)
#
# ... и так далее для других функций.


def get_faq_answer(question: str, user_info: dict) -> str:
    prompt = f"Пользователь {user_info.get('username', 'аноним')} задает вопрос о сайте Chatty Orange: '{question}'. Ответь на этот вопрос подробно и дружелюбно. Если вопрос не по теме сайта Chatty Orange или его функционала, вежливо укажи на это. При необходимости, можешь предположить, что Chatty Orange - это социальная сеть со стандартным набором функций (посты, лайки, комментарии, подписки, профили пользователей)."
    return get_gemini_response(prompt)

def get_feature_explanation(feature_query: str, user_info: dict) -> str:
    prompt = f"Пользователь {user_info.get('username', 'аноним')} спрашивает о функции '{feature_query}' на сайте Chatty Orange. Подробно объясни, что это за функция, как ею пользоваться, и какие преимущества она дает. Если точное название функции неизвестно, но понятен контекст из запроса '{feature_query}', объясни наиболее подходящую по смыслу функцию. Chatty Orange - это социальная сеть."
    return get_gemini_response(prompt)