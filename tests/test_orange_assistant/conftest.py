import pytest
from unittest.mock import patch, Mock
from django.test import override_settings
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_cache():
    """Автоматически очищает кеш перед каждым тестом Orange Assistant."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def mock_gemini_api():
    """Мок для Google Gemini API с различными типами ответов."""
    with patch('orange_assistant.ai_services.genai') as mock_genai:
        # Настраиваем мок модели
        mock_model = Mock()
        mock_response = Mock()

        # Стандартный ответ через parts
        mock_part = Mock()
        mock_part.text = "Мокированный ответ от Gemini"
        mock_response.parts = [mock_part]
        mock_response.text = "Мокированный ответ от Gemini"

        # Альтернативный ответ через candidates (для тестирования разных путей)
        mock_candidate = Mock()
        mock_content = Mock()
        mock_content.parts = [mock_part]
        mock_candidate.content = mock_content
        mock_response.candidates = [mock_candidate]

        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        yield mock_genai


@pytest.fixture
def mock_gemini_response():
    """Мок для функции get_gemini_response."""
    with patch('orange_assistant.ai_services.get_gemini_response') as mock:
        mock.return_value = "Тестовый ответ от ИИ"
        yield mock


@pytest.fixture
def mock_gemini_error():
    """Мок для тестирования ошибок Gemini API."""
    with patch('orange_assistant.ai_services.genai') as mock_genai:
        mock_genai.configure.side_effect = Exception("API connection error")
        yield mock_genai


@pytest.fixture
def ai_chat_data():
    """Базовые данные для тестирования чата с ИИ."""
    return {
        'user_input': 'Тестовое сообщение',
        'action_type': 'general_chat'
    }


@pytest.fixture
def find_user_data():
    """Данные для тестирования поиска пользователя."""
    return {
        'user_input': 'найди пользователя testuser',
        'action_type': 'find_user_by_username'
    }


@pytest.fixture
def find_post_data():
    """Данные для тестирования поиска постов."""
    return {
        'user_input': 'найди посты про Django',
        'action_type': 'find_post_by_keyword'
    }


@pytest.fixture
def check_content_data():
    """Данные для тестирования проверки контента."""
    return {
        'user_input': 'проверь мой пост',
        'action_type': 'check_post_content'
    }


@pytest.fixture
def interactive_tour_data():
    """Данные для тестирования интерактивного тура."""
    return {
        'user_input': 'покажи тур',
        'action_type': 'interactive_tour_step',
        'step_number': 1
    }


@pytest.fixture
def subscription_recommendations_data():
    """Данные для тестирования рекомендаций подписок."""
    return {
        'user_input': 'кого почитать?',
        'action_type': 'subscription_recommendations'
    }


@pytest.fixture
def post_creation_suggestion_data():
    """Данные для тестирования предложений создания постов."""
    return {
        'user_input': 'помоги с постом',
        'action_type': 'post_creation_suggestion',
        'current_text': 'Мой черновик поста'
    }


@pytest.fixture
def analyze_profile_data():
    """Данные для тестирования анализа профиля."""
    return {
        'user_input': 'проанализируй мой профиль',
        'action_type': 'analyze_profile'
    }


@pytest.fixture
def generate_post_ideas_data():
    """Данные для тестирования генерации идей постов."""
    return {
        'user_input': 'дай идеи для постов',
        'action_type': 'generate_post_ideas',
        'tags': ['Python', 'Django']
    }


@pytest.fixture
def analyze_sentiment_data():
    """Данные для тестирования анализа настроения."""
    return {
        'user_input': 'Я очень рад сегодня!',
        'action_type': 'analyze_sentiment'
    }


@pytest.fixture
def get_post_details_data():
    """Данные для тестирования получения деталей поста."""
    return {
        'user_input': 'покажи пост 1',
        'action_type': 'get_post_details',
        'post_id': 1
    }


@pytest.fixture
def get_user_activity_data():
    """Данные для тестирования получения активности пользователя."""
    return {
        'user_input': 'активность пользователя 1',
        'action_type': 'get_user_activity',
        'user_id_target': 1
    }


@pytest.fixture
def faq_data():
    """Данные для тестирования FAQ."""
    return {
        'user_input': 'как создать пост?',
        'action_type': 'faq'
    }


@pytest.fixture
def feature_explanation_data():
    """Данные для тестирования объяснения функций."""
    return {
        'user_input': 'как работают лайки?',
        'action_type': 'feature_explanation'
    }


@pytest.fixture
def api_key_settings():
    """Настройки с валидным API ключом."""
    with override_settings(GOOGLE_API_KEY='test-api-key-12345'):
        yield


@pytest.fixture
def no_api_key_settings():
    """Настройки без API ключа."""
    with override_settings(GOOGLE_API_KEY=None):
        yield


@pytest.fixture
def assistant_user_info():
    """Информация о пользователе для AI сервисов."""
    return {
        'user_id': 1,
        'username': 'testuser',
        'email': 'testuser@example.com',
        'is_authenticated': True
    }


@pytest.fixture
def anonymous_user_info():
    """Информация для анонимного пользователя."""
    return {
        'user_id': None,
        'username': 'Гость',
        'email': '',
        'is_authenticated': False
    }


@pytest.fixture
def rate_limit_settings():
    """Настройки для тестирования rate limiting."""
    return {
        'max_requests': 5,  # Меньший лимит для быстрого тестирования
        'window': 60
    }


@pytest.fixture
def mock_all_ai_services():
    """Мокает все AI сервисы для изоляции тестов."""
    services_to_mock = [
        'orange_assistant.views.get_faq_answer',
        'orange_assistant.views.get_feature_explanation',
        'orange_assistant.views.get_interactive_tour_step',
        'orange_assistant.views.get_post_creation_suggestion',
        'orange_assistant.views.get_subscription_recommendations',
        'orange_assistant.views.check_post_content',
        'orange_assistant.views.analyze_profile_stats',
        'orange_assistant.views.generate_post_ideas',
        'orange_assistant.views.analyze_sentiment',
        'orange_assistant.views.find_post_by_keyword',
        'orange_assistant.views.get_post_details',
        'orange_assistant.views.find_user_by_username',
        'orange_assistant.views.get_user_activity',
        'orange_assistant.views.get_gemini_response'
    ]

    mocks = {}
    for service in services_to_mock:
        mock_path = patch(service)
        mock_obj = mock_path.start()
        mock_obj.return_value = f"Мокированный ответ для {service.split('.')[-1]}"
        mocks[service] = mock_obj

    yield mocks

    # Останавливаем все моки
    for service in services_to_mock:
        patch.stopall()


@pytest.fixture
def natural_language_test_cases():
    """Тестовые случаи для обработки естественного языка."""
    return {
        'user_search': [
            'найди пользователя admin',
            'профиль Orange',
            'кто такой testuser',
            '@developer'
        ],
        'post_search': [
            'найди пост Django',
            'найди посты про Python',
            'пост (веб-разработка)',
            'покажи пост машинное обучение'
        ],
        'user_posts': [
            'статьи у Orange',
            'посты пользователя admin',
            'что писал developer',
            'какие статьи у Orange'
        ],
        'post_details': [
            'расскажи о посте 5',
            'покажи пост 10',
            'детали поста 1',
            'что в посте номер 3'
        ],
        'recommendations': [
            'кого почитать',
            'рекомендации авторов',
            'посоветуй подписки',
            'интересные авторы'
        ],
        'general_chat': [
            'привет',
            'как дела',
            'что нового',
            'расскажи о себе'
        ]
    }


@pytest.fixture
def long_text_samples():
    """Образцы длинных текстов для тестирования лимитов."""
    return {
        'short': 'Короткий текст',
        'medium': 'А' * 500,
        'long': 'Б' * 2000,
        'very_long': 'В' * 5000,
        'excessive': 'Г' * 10000
    }


@pytest.fixture
def mock_database_queries():
    """Мок для тестирования без реальных запросов к БД."""
    with patch('posts.models.Post.objects') as mock_post_objects, \
            patch('users.models.CustomUser.objects') as mock_user_objects, \
            patch('subscriptions.models.Subscription.objects') as mock_sub_objects:
        # Настраиваем стандартные ответы
        mock_post_objects.filter.return_value.exists.return_value = False
        mock_user_objects.get.side_effect = Exception("User not found")
        mock_sub_objects.filter.return_value.count.return_value = 0

        yield {
            'posts': mock_post_objects,
            'users': mock_user_objects,
            'subscriptions': mock_sub_objects
        }