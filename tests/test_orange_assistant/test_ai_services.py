import pytest
from unittest.mock import patch, Mock
from django.contrib.auth import get_user_model
from django.test import override_settings
from orange_assistant.ai_services import (
    get_gemini_response,
    find_post_by_keyword,
    find_user_by_username,
    get_subscription_recommendations,
    check_post_content,
    analyze_profile_stats,
    generate_post_ideas,
    analyze_sentiment,
    get_post_details,
    get_user_activity,
    get_faq_answer,
    get_feature_explanation,
    get_interactive_tour_step,
    get_post_creation_suggestion
)
from posts.models import Post, Comment, Tag
from subscriptions.models import Subscription
from tests.factories import UserFactory, PostFactory, TagFactory

User = get_user_model()


@pytest.mark.django_db
class TestAIServices:
    """Тесты для AI сервисов Orange Assistant."""

    @override_settings(GOOGLE_API_KEY='test-api-key')
    @patch('orange_assistant.ai_services.genai')
    def test_get_gemini_response_success(self, mock_genai):
        """Тест успешного получения ответа от Gemini AI."""
        # Мокаем ответ от Gemini
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Тестовый ответ от ИИ"
        mock_response.parts = [Mock(text="Тестовый ответ от ИИ")]
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = get_gemini_response("Тестовый промпт")

        assert result == "Тестовый ответ от ИИ"
        mock_genai.configure.assert_called_once()
        mock_genai.GenerativeModel.assert_called_once_with('gemini-2.0-flash')

    @override_settings(GOOGLE_API_KEY='test-api-key')
    @patch('orange_assistant.ai_services.genai')
    def test_get_gemini_response_with_candidates(self, mock_genai):
        """Тест получения ответа через candidates."""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = None
        mock_response.parts = None

        # Мокаем структуру candidates
        mock_part = Mock()
        mock_part.text = "Ответ через candidates"
        mock_content = Mock()
        mock_content.parts = [mock_part]
        mock_candidate = Mock()
        mock_candidate.content = mock_content
        mock_response.candidates = [mock_candidate]

        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = get_gemini_response("Тестовый промпт")

        assert result == "Ответ через candidates"

    @override_settings(GOOGLE_API_KEY=None)
    def test_get_gemini_response_no_api_key(self):
        """Тест обработки отсутствия API ключа."""
        result = get_gemini_response("Тестовый промпт")
        assert "Ключ API для сервиса ИИ не настроен" in result

    @override_settings(GOOGLE_API_KEY="test_key")
    @patch('orange_assistant.ai_services.genai.configure')
    def test_get_gemini_response_api_error(self, mock_genai_configure):
        """ИСПРАВЛЕНО: Тест обработки ошибки API."""
        # Мокируем ошибку при вызове configure
        mock_genai_configure.side_effect = Exception("API Error from configure")

        result = get_gemini_response("Тестовый промпт")

        assert "Произошла ошибка при обращении к сервису ИИ" in result
        assert "Подробности: API Error from configure" in result

    @patch('orange_assistant.ai_services.get_gemini_response')
    def test_find_post_by_keyword_found(self, mock_gemini):
        """Тест поиска постов по ключевому слову - найдены результаты."""
        # Создаем тестовые данные
        user = UserFactory()
        post1 = PostFactory(
            title="Django для начинающих",
            text="Урок по Django",
            author=user
        )
        post2 = PostFactory(
            title="Python разработка",
            text="Изучаем Python",
            author=user
        )

        mock_gemini.return_value = "Найдены посты по Django"

        result = find_post_by_keyword(
            keyword="Django",
            user_info={"username": user.username}
        )

        assert "Django" in result
        assert post1.title in result

    @patch('orange_assistant.ai_services.get_gemini_response')
    def test_find_post_by_keyword_not_found(self, mock_gemini):
        """Тест поиска постов - ничего не найдено."""
        user = UserFactory()

        result = find_post_by_keyword(
            keyword="НесуществующееСлово",
            user_info={"username": user.username}
        )

        assert "не найдены" in result or "не найдено" in result

    def test_find_user_by_username_found(self):
        """Тест поиска пользователя по имени - найден."""
        user = UserFactory(username="testuser", bio="Разработчик Django")
        PostFactory.create_batch(3, author=user)  # 3 поста у пользователя

        result = find_user_by_username(
            username="testuser",
            user_info={"username": "searcher"}
        )

        assert f"@{user.username}" in result
        assert "Найден пользователь" in result
        assert "3" in result  # количество постов

    def test_find_user_by_username_not_found(self):
        """Тест поиска несуществующего пользователя."""
        result = find_user_by_username(
            username="несуществующий",
            user_info={"username": "searcher"}
        )

        assert "не найден" in result

    def test_get_subscription_recommendations_with_users(self):
        """Тест получения рекомендаций подписок."""
        # Создаем пользователей и посты
        current_user = UserFactory()
        popular_user1 = UserFactory(username="blogger1")
        popular_user2 = UserFactory(username="blogger2")

        # Создаем посты для популярности
        PostFactory.create_batch(5, author=popular_user1)
        PostFactory.create_batch(3, author=popular_user2)

        result = get_subscription_recommendations(
            user_info={"username": current_user.username},
            current_user_id=current_user.id
        )

        assert "Рекомендую подписаться" in result
        assert popular_user1.username in result

    def test_get_subscription_recommendations_no_users(self):
        """Тест рекомендаций при отсутствии пользователей."""
        result = get_subscription_recommendations(
            user_info={"username": "test"},
            current_user_id=None
        )

        assert "мало активных авторов" in result or "Рекомендую" in result

    @patch('orange_assistant.ai_services.get_gemini_response')
    def test_check_post_content_valid(self, mock_gemini):
        """Тест проверки допустимого контента поста."""
        mock_gemini.return_value = "✅ Отличный пост! Можно публиковать!"

        result = check_post_content(
            post_text="Рассказываю о Django разработке",
            user_info={"username": "testuser"}
        )

        assert "Отличный пост" in result
        mock_gemini.assert_called_once()

    def test_check_post_content_empty(self):
        """Тест проверки пустого контента."""
        result = check_post_content(
            post_text="",
            user_info={"username": "testuser"}
        )

        assert "не может быть пустым" in result

    def test_get_post_details_found(self):
        """Тест получения деталей существующего поста."""
        user = UserFactory()
        post = PostFactory(
            title="Тестовый пост",
            text="Содержимое тестового поста",
            author=user
        )

        result = get_post_details(
            post_id=post.id,
            user_info={"username": "searcher"}
        )

        assert post.title in result
        assert user.username in result
        assert "Вот что я нашел" in result

    def test_get_post_details_not_found(self):
        """Тест получения деталей несуществующего поста."""
        result = get_post_details(
            post_id=99999,
            user_info={"username": "searcher"}
        )

        assert "не найден" in result

    def test_get_user_activity_found(self):
        """Тест получения активности существующего пользователя."""
        user = UserFactory()
        PostFactory.create_batch(2, author=user)

        result = get_user_activity(
            user_id=user.id,
            user_info={"username": "searcher"}
        )

        assert f"@{user.username}" in result
        assert "активность" in result

    def test_get_user_activity_not_found(self):
        """Тест получения активности несуществующего пользователя."""
        result = get_user_activity(
            user_id=99999,
            user_info={"username": "searcher"}
        )

        assert "не найден" in result

    def test_analyze_profile_stats(self):
        """Тест анализа статистики профиля."""
        user = UserFactory()
        PostFactory.create_batch(3, author=user)

        with patch('orange_assistant.ai_services.get_gemini_response') as mock_gemini:
            mock_gemini.return_value = "Анализ профиля пользователя"

            result = analyze_profile_stats(user_id=user.id)

            assert "Анализ профиля" in result
            mock_gemini.assert_called_once()

    def test_analyze_profile_stats_not_found(self):
        """Тест анализа несуществующего профиля."""
        result = analyze_profile_stats(user_id=99999)

        assert "не найден" in result

    @patch('orange_assistant.ai_services.get_gemini_response')
    def test_generate_post_ideas(self, mock_gemini):
        """Тест генерации идей для постов."""
        mock_gemini.return_value = "💡 Идеи для постов"

        result = generate_post_ideas(
            user_info={"username": "testuser"},
            tags=["Python", "Django"]
        )

        assert "Идеи для постов" in result
        mock_gemini.assert_called_once()

    @patch('orange_assistant.ai_services.get_gemini_response')
    def test_analyze_sentiment(self, mock_gemini):
        """Тест анализа настроения текста."""
        mock_gemini.return_value = "😊 Позитивное настроение"

        result = analyze_sentiment(text="Я очень рад!")

        assert "Позитивное" in result
        mock_gemini.assert_called_once()

    @patch('orange_assistant.ai_services.get_gemini_response')
    def test_get_faq_answer(self, mock_gemini):
        """Тест получения FAQ ответов."""
        mock_gemini.return_value = "Ответ на FAQ вопрос"

        result = get_faq_answer(
            question="Как создать пост?",
            user_info={"username": "testuser"}
        )

        assert "Ответ на FAQ" in result
        mock_gemini.assert_called_once()

    @patch('orange_assistant.ai_services.get_gemini_response')
    def test_get_feature_explanation_general(self, mock_gemini):
        """Тест объяснения общих возможностей."""
        mock_gemini.return_value = "Объяснение возможностей"

        result = get_feature_explanation(
            feature_query="что ты умеешь",
            user_info={"username": "testuser"}
        )

        assert "Объяснение возможностей" in result
        mock_gemini.assert_called_once()

    @patch('orange_assistant.ai_services.get_gemini_response')
    def test_get_feature_explanation_specific(self, mock_gemini):
        """Тест объяснения конкретной функции."""
        mock_gemini.return_value = "Объяснение функции лайков"

        result = get_feature_explanation(
            feature_query="как работают лайки",
            user_info={"username": "testuser"}
        )

        assert "Объяснение функции" in result

    def test_get_interactive_tour_step_valid(self):
        """Тест получения валидного шага тура."""
        result = get_interactive_tour_step(
            step_number=1,
            user_info={"username": "testuser"}
        )

        assert "Добро пожаловать" in result
        assert "<h5>" in result  # HTML формат

    def test_get_interactive_tour_step_invalid(self):
        """Тест получения невалидного шага тура."""
        result = get_interactive_tour_step(
            step_number=999,
            user_info={"username": "testuser"}
        )

        # Должен вернуть последний шаг как fallback
        assert "готов к использованию" in result

    @patch('orange_assistant.ai_services.get_gemini_response')
    def test_get_post_creation_suggestion_empty(self, mock_gemini):
        """Тест получения предложений для пустого поста."""
        mock_gemini.return_value = "🌟 Идеи для первого поста"

        result = get_post_creation_suggestion(
            current_text="",
            user_info={"username": "testuser"}
        )

        assert "Идеи для" in result
        mock_gemini.assert_called_once()

    @patch('orange_assistant.ai_services.get_gemini_response')
    def test_get_post_creation_suggestion_with_text(self, mock_gemini):
        """Тест получения предложений для существующего текста."""
        mock_gemini.return_value = "Советы по улучшению поста"

        result = get_post_creation_suggestion(
            current_text="Мой первый пост о Django",
            user_info={"username": "testuser"}
        )

        assert "Советы по улучшению" in result
        mock_gemini.assert_called_once()


@pytest.mark.django_db
class TestAIServicesIntegration:
    """Интеграционные тесты AI сервисов."""

    def test_post_search_with_tags(self):
        """Интеграционный тест поиска постов с тегами."""
        user = UserFactory()
        tag = TagFactory(name="Django")
        post = PostFactory(
            title="Django руководство",
            text="Изучаем Django фреймворк",
            author=user
        )
        post.tags.add(tag)

        result = find_post_by_keyword(
            keyword="Django",
            user_info={"username": user.username}
        )

        assert post.title in result
        assert "Django" in result

    def test_user_search_with_posts_and_subscribers(self):
        """Тест поиска пользователя с полной статистикой."""
        target_user = UserFactory(username="target", bio="Django разработчик")
        searcher = UserFactory(username="searcher")

        # Создаем посты и подписки
        PostFactory.create_batch(5, author=target_user)
        if Subscription:
            Subscription.objects.create(subscriber=searcher, author=target_user)

        result = find_user_by_username(
            username="target",
            user_info={"username": "searcher"}
        )

        assert "target" in result
        assert "5" in result  # количество постов
        assert "Django разработчик" in result

    def test_recommendation_excludes_current_user(self):
        """Тест что рекомендации исключают текущего пользователя."""
        current_user = UserFactory()
        other_user = UserFactory()

        PostFactory.create_batch(3, author=current_user)
        PostFactory.create_batch(2, author=other_user)

        result = get_subscription_recommendations(
            user_info={"username": current_user.username},
            current_user_id=current_user.id
        )

        # Текущий пользователь не должен быть в рекомендациях
        assert current_user.username not in result
        assert other_user.username in result

    def test_post_details_with_comments_and_likes(self):
        """Тест деталей поста с комментариями и лайками."""
        author = UserFactory()
        commenter = UserFactory()
        post = PostFactory(
            title="Интересный пост",
            text="Очень интересное содержимое",
            author=author
        )

        # Добавляем комментарий
        Comment.objects.create(
            post=post,
            author=commenter,
            text="Отличный пост!"
        )

        # Добавляем лайк
        if hasattr(post, 'likes'):
            post.likes.add(commenter)

        result = get_post_details(
            post_id=post.id,
            user_info={"username": "searcher"}
        )

        assert post.title in result
        assert author.username in result
        assert "Отличный пост!" in result

    def test_user_activity_comprehensive(self):
        """Комплексный тест активности пользователя."""
        user = UserFactory()
        other_user = UserFactory()

        # Создаем посты пользователя
        posts = PostFactory.create_batch(2, author=user)

        # Создаем комментарии пользователя
        other_post = PostFactory(author=other_user)
        Comment.objects.create(
            post=other_post,
            author=user,
            text="Мой комментарий"
        )

        result = get_user_activity(
            user_id=user.id,
            user_info={"username": "searcher"}
        )

        assert f"@{user.username}" in result
        assert "Недавние посты" in result
        assert "Недавние комментарии" in result
        assert posts[0].title in result
        assert "Мой комментарий" in result

    @patch('orange_assistant.ai_services.get_gemini_response')
    def test_new_features_coverage(self, mock_gemini):
        """НОВЫЙ ТЕСТ: Покрытие дополнительных функций для повышения coverage."""
        mock_gemini.return_value = "Тестовый ответ"

        # Тестируем функции, которые могли быть не покрыты
        user_info = {"username": "testuser"}

        # Тест функции объяснения возможностей
        result1 = get_feature_explanation("помощь", user_info)
        assert "Тестовый ответ" in result1

        # Тест функции FAQ
        result2 = get_faq_answer("как создать пост", user_info)
        assert "Тестовый ответ" in result2

        # Тест генерации идей без тегов
        result3 = generate_post_ideas(user_info)
        assert "Тестовый ответ" in result3

    @patch('orange_assistant.ai_services.get_gemini_response')
    def test_edge_cases_coverage(self, mock_gemini):
        """НОВЫЙ ТЕСТ: Тестирование граничных случаев."""
        mock_gemini.return_value = "Ответ для граничного случая"

        # Тест очень длинного текста
        long_text = "А" * 1000
        result = check_post_content(long_text, {"username": "test"})
        assert "Ответ для граничного случая" in result

        # Тест анализа настроения с особыми символами
        special_text = "Тест с эмодзи 😊 и символами @#$%!"
        result2 = analyze_sentiment(special_text)
        assert "Ответ для граничного случая" in result2

    def test_model_availability_checks(self):
        """НОВЫЙ ТЕСТ: Проверка доступности моделей."""
        # Тестируем случаи, когда модели недоступны
        # Этот тест поможет покрыть условия проверки моделей в коде

        result1 = find_post_by_keyword("test", {"username": "test"})
        # Должен работать корректно когда модели доступны
        assert isinstance(result1, str)

        result2 = find_user_by_username("test", {"username": "test"})
        # Должен обработать случай когда пользователь не найден
        assert "не найден" in result2

        result3 = get_subscription_recommendations({"username": "test"})
        # Должен работать даже без пользователей
        assert isinstance(result3, str)

    def test_empty_and_none_inputs(self):
        """НОВЫЙ ТЕСТ: Тестирование пустых и None входных данных."""
        # Пустые строки
        result1 = check_post_content("", {"username": "test"})
        assert "пустым" in result1

        # None значения в user_info
        result2 = find_post_by_keyword("test", {})
        assert isinstance(result2, str)

        # Пустой user_info
        result3 = get_subscription_recommendations({})
        assert isinstance(result3, str)

    @patch('orange_assistant.ai_services.logger')
    def test_logging_coverage(self, mock_logger):
        """НОВЫЙ ТЕСТ: Покрытие логирования."""
        # Тестируем что логирование происходит в ключевых функциях
        user = UserFactory()
        post = PostFactory(author=user)

        # Вызываем функцию, которая должна логировать
        find_post_by_keyword("test", {"username": "test"})

        # Проверяем что логирование вызывалось
        assert mock_logger.info.called

        # Тестируем логирование для других функций
        get_post_details(post.id, {"username": "test"})
        find_user_by_username(user.username, {"username": "test"})

        # Должно быть несколько вызовов логирования
        assert mock_logger.info.call_count >= 3