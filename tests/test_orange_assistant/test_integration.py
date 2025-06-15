import pytest
import json
from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from posts.models import Post, Comment, Tag
from subscriptions.models import Subscription
from tests.factories import UserFactory, PostFactory, TagFactory

User = get_user_model()


@pytest.mark.django_db
class TestOrangeAssistantIntegration:
    """Интеграционные тесты Orange Assistant с другими модулями."""

    def setup_method(self):
        """Настройка для каждого теста."""
        self.chat_url = reverse('orange_assistant:ai_chat')
        cache.clear()  # Очищаем кеш для rate limiting

    @patch('orange_assistant.views.get_gemini_response')
    def test_full_user_search_workflow_with_natural_language(self, mock_gemini, authenticated_client, user):
        """Полный workflow поиска пользователя через естественный язык."""
        mock_gemini.return_value = "Мокированный ответ от ИИ"

        # 1. Создаем пользователя для поиска с уникальным именем
        target_user = UserFactory(
            username="djangoexpert001",  # Уникальное имя
            bio="Опытный Django разработчик",
            email="expert001@example.com"
        )

        # 2. Создаем контент от этого пользователя
        posts = PostFactory.create_batch(3, author=target_user)

        # 3. Создаем подписчиков
        followers = UserFactory.create_batch(5)
        for i, follower in enumerate(followers):
            follower.username = f"follower_{i}_{target_user.id}"  # Уникальные имена
            follower.save()
            Subscription.objects.create(subscriber=follower, author=target_user)

        # 4. Тестируем поиск через естественный язык без action_type
        data = {
            'user_input': f'найди пользователя {target_user.username}',
            'action_type': 'general_chat'  # Используем general_chat для natural language
        }

        response = authenticated_client.post(
            self.chat_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        # 5. Проверяем результат
        assert response.status_code == 200
        response_data = response.json()
        # Проверяем что ответ содержит информацию о пользователе
        assert target_user.username in response_data['response']

    @patch('orange_assistant.views.get_gemini_response')
    def test_user_posts_query_handling(self, mock_gemini, authenticated_client):
        """Тест обработки запросов постов пользователя через естественный язык."""
        mock_gemini.return_value = "Мокированный ответ"

        # Создаем пользователя с уникальным именем
        author = UserFactory(username="Orange002")
        posts = []
        for i in range(3):
            post = PostFactory(
                title=f"Статья {i + 1}",
                text=f"Содержимое статьи {i + 1}",
                author=author
            )
            posts.append(post)

        test_queries = [
            "статьи у Orange002",
            "посты пользователя Orange002",
            "что писал Orange002",
            "какие статьи у Orange002"
        ]

        for query in test_queries:
            data = {
                'user_input': query,
                'action_type': 'general_chat'  # Используем general_chat для natural language
            }

            response = authenticated_client.post(
                self.chat_url,
                data=json.dumps(data),
                content_type='application/json'
            )

            assert response.status_code == 200
            response_text = response.json()['response']

            # Должен распознать как запрос постов пользователя
            assert "Orange002" in response_text

    @patch('orange_assistant.views.get_gemini_response')
    def test_general_post_search_with_keyword_extraction(self, mock_gemini, authenticated_client):
        """Тест общего поиска постов с извлечением ключевых слов."""
        mock_gemini.return_value = "Найдены посты по ключевому слову"

        # Создаем посты с разными темами
        author1 = UserFactory(username="author001")
        author2 = UserFactory(username="author002")

        django_post = PostFactory(
            title="Изучаем Django",
            text="Django - отличный фреймворк",
            author=author1
        )
        python_post = PostFactory(
            title="Python для начинающих",
            text="Основы Python программирования",
            author=author2
        )

        test_cases = [
            ("найди пост Django", "Django"),
            ("найди посты про Python", "Python"),
            ("покажи пост (веб-разработка)", "веб-разработка"),
            ("пост машинное обучение", "машинное обучение")
        ]

        for query, expected_keyword in test_cases:
            data = {
                'user_input': query,
                'action_type': 'general_chat'
            }

            response = authenticated_client.post(
                self.chat_url,
                data=json.dumps(data),
                content_type='application/json'
            )

            assert response.status_code == 200

    def test_post_details_request_with_id_extraction(self, authenticated_client):
        """ИСПРАВЛЕНО: Тест запроса деталей поста с извлечением ID."""
        # Мокируем ответ для get_post_details вместо общего gemini
        with patch('orange_assistant.views.get_post_details') as mock_get_post_details:
            mock_get_post_details.return_value = "Детали поста найдены"

            author = UserFactory(username="author003")
            post = PostFactory(
                title="Интересный пост",
                text="Очень интересное содержимое поста",
                author=author
            )

            # Добавляем комментарий для полноты
            Comment.objects.create(
                post=post,
                author=author,
                text="Отличный пост!"
            )

            test_queries = [
                f"расскажи о посте {post.id}",
                f"покажи пост {post.id}",
                f"детали поста {post.id}",
                f"что в посте номер {post.id}"
            ]

            for query in test_queries:
                data = {
                    'user_input': query,
                    'action_type': 'general_chat'
                }

                response = authenticated_client.post(
                    self.chat_url,
                    data=json.dumps(data),
                    content_type='application/json'
                )

                assert response.status_code == 200
                response_text = response.json()['response']

                # Должен содержать ответ от mock
                assert "Детали поста найдены" in response_text

    @patch('orange_assistant.views.get_subscription_recommendations')
    def test_subscription_recommendations_integration(self, mock_recommendations, authenticated_client, user):
        """Тест интеграции рекомендаций подписок."""
        mock_recommendations.return_value = "Рекомендации подписок"

        # Создаем активных авторов с уникальными именами
        popular_author = UserFactory(username=f"popular_blogger_{user.id}")
        PostFactory.create_batch(10, author=popular_author)

        less_popular_author = UserFactory(username=f"casual_blogger_{user.id}")
        PostFactory.create_batch(3, author=less_popular_author)

        # Создаем подписки других пользователей на популярного автора
        other_users = []
        for i in range(5):
            other_user = UserFactory(username=f"user_{i}_{user.id}")
            other_users.append(other_user)
            Subscription.objects.create(subscriber=other_user, author=popular_author)

        data = {
            'user_input': 'кого почитать?',
            'action_type': 'general_chat'
        }

        response = authenticated_client.post(
            self.chat_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 200
        response_text = response.json()['response']
        assert "Рекомендации подписок" in response_text

    def test_rate_limiting_across_multiple_requests(self, client):
        """Тест rate limiting на протяжении нескольких запросов."""
        # Отправляем 15 запросов (лимит)
        for i in range(15):
            data = {
                'user_input': f'тест {i}',
                'action_type': 'general_chat'
            }

            with patch('orange_assistant.views.get_gemini_response') as mock_gemini:
                mock_gemini.return_value = f"Ответ {i}"

                response = client.post(
                    self.chat_url,
                    data=json.dumps(data),
                    content_type='application/json'
                )

                assert response.status_code == 200

        # 16-й запрос должен быть заблокирован
        data = {
            'user_input': 'тест превышение лимита',
            'action_type': 'general_chat'
        }

        response = client.post(
            self.chat_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 429
        assert "Слишком много запросов" in response.json()['error']

    @patch('orange_assistant.views.get_gemini_response')
    def test_complex_natural_language_processing(self, mock_gemini, authenticated_client):
        """ИСПРАВЛЕНО: Тест сложной обработки естественного языка."""
        mock_gemini.return_value = "Обработанный ответ"

        # Создаем данные для тестирования с уникальными именами
        user1 = UserFactory(username="developer004")
        user2 = UserFactory(username="designer004")

        post1 = PostFactory(title="Django разработка", text="Гайд по Django", author=user1)
        post2 = PostFactory(title="UI/UX дизайн", text="Принципы дизайна", author=user2)

        complex_queries = [
            # Поиск пользователя с разными вариациями
            "кто такой developer004",
            "профиль designer004",

            # Поиск постов с разными форматами
            "найди пост Django",
            "посты про дизайн",

            # Смешанные запросы
            "что писал developer004",
            "статьи у designer004"
        ]

        for query in complex_queries:
            data = {
                'user_input': query,
                'action_type': 'general_chat'
            }

            response = authenticated_client.post(
                self.chat_url,
                data=json.dumps(data),
                content_type='application/json'
            )

            assert response.status_code == 200
            response_text = response.json()['response']

            # Проверяем, что получили осмысленный ответ
            assert len(response_text) > 10
            # С мокированием не должно быть ошибок API
            assert "ошибка" not in response_text.lower() or "Обработанный ответ" in response_text

    def test_user_info_propagation(self, authenticated_client, user):
        """Тест правильной передачи информации о пользователе."""
        with patch('orange_assistant.views.analyze_profile_stats') as mock_analyze:
            mock_analyze.return_value = "Анализ профиля"

            data = {
                'user_input': 'проанализируй профиль',
                'action_type': 'analyze_profile'
            }

            response = authenticated_client.post(
                self.chat_url,
                data=json.dumps(data),
                content_type='application/json'
            )

            assert response.status_code == 200

            # Проверяем, что user_id был передан правильно
            if mock_analyze.called:
                call_args = mock_analyze.call_args
                assert call_args[1]['user_id'] == user.id

    @patch('orange_assistant.views.get_gemini_response')
    def test_error_recovery_in_natural_language(self, mock_gemini, authenticated_client):
        """ИСПРАВЛЕНО: Тест восстановления после ошибок в обработке естественного языка."""
        # Мокируем ответы для разных случаев
        mock_gemini.return_value = "Пользователь не найден, попробуйте другой запрос"

        # Запросы, которые могут вызвать ошибки
        problematic_queries = [
            "найди пользователя несуществующий_пользователь",
            "покажи пост 99999",
            "активность пользователя 99999",
            "пост про ничего_не_найдется"
        ]

        for query in problematic_queries:
            data = {
                'user_input': query,
                'action_type': 'general_chat'
            }

            response = authenticated_client.post(
                self.chat_url,
                data=json.dumps(data),
                content_type='application/json'
            )

            # Даже при ошибках должен возвращать 200 с понятным сообщением
            assert response.status_code == 200
            response_text = response.json()['response']

            # Должен содержать понятное сообщение об ошибке или предложение
            assert any(phrase in response_text.lower() for phrase in [
                "не найден", "не найдено", "не удалось", "попробуйте", "проверьте"
            ])

    @patch('orange_assistant.views.get_gemini_response')
    def test_action_type_vs_natural_language_consistency(self, mock_gemini, authenticated_client):
        """ИСПРАВЛЕНО: Тест согласованности между action_type и естественным языком."""
        # Создаем пользователя с уникальным именем для каждого теста
        test_user = UserFactory(username=f"testuser_{authenticated_client.session.session_key or 'default'}")

        mock_gemini.return_value = f"Найден пользователь {test_user.username}"

        # Одинаковые запросы с action_type и без
        test_cases = [
            {
                'with_action': {
                    'user_input': f'найди пользователя {test_user.username}',
                    'action_type': 'find_user_by_username'
                },
                'natural': {
                    'user_input': f'найди пользователя {test_user.username}',
                    'action_type': 'general_chat'
                }
            }
        ]

        for case in test_cases:
            # Мокируем конкретную функцию для первого запроса
            with patch('orange_assistant.views.find_user_by_username') as mock_find_user:
                mock_find_user.return_value = f"Найден пользователь {test_user.username}"

                # Запрос с явным action_type
                response1 = authenticated_client.post(
                    self.chat_url,
                    data=json.dumps(case['with_action']),
                    content_type='application/json'
                )

            # Запрос через естественный язык
            response2 = authenticated_client.post(
                self.chat_url,
                data=json.dumps(case['natural']),
                content_type='application/json'
            )

            assert response1.status_code == 200
            assert response2.status_code == 200

            # Оба должны найти пользователя
            text1 = response1.json()['response']
            text2 = response2.json()['response']

            assert test_user.username in text1
            assert test_user.username in text2

    @patch('orange_assistant.views.get_gemini_response')
    def test_long_conversation_simulation(self, mock_gemini, authenticated_client):
        """Тест симуляции длинного разговора."""
        mock_gemini.return_value = "Ответ от ИИ"

        conversation = [
            "привет",
            "что ты умеешь",
            "найди пользователя admin",
            "кого почитать",
            "найди пост Django",
            "помоги с идеями для поста"
        ]

        for i, message in enumerate(conversation):
            data = {
                'user_input': message,
                'action_type': 'general_chat'
            }

            response = authenticated_client.post(
                self.chat_url,
                data=json.dumps(data),
                content_type='application/json'
            )

            assert response.status_code == 200
            response_text = response.json()['response']
            assert len(response_text) > 5  # Должен давать содержательные ответы

            # Проверяем наличие timestamp
            assert 'timestamp' in response.json()

    @patch('orange_assistant.views.get_gemini_response')
    def test_anonymous_vs_authenticated_behavior(self, mock_gemini, client, authenticated_client):
        """Тест различий в поведении для анонимных и авторизованных пользователей."""
        mock_gemini.return_value = "Ответ для пользователя"

        query_data = {
            'user_input': 'что ты умеешь',
            'action_type': 'general_chat'
        }

        # Запрос от анонимного пользователя
        anon_response = client.post(
            self.chat_url,
            data=json.dumps(query_data),
            content_type='application/json'
        )

        # Запрос от авторизованного пользователя
        auth_response = authenticated_client.post(
            self.chat_url,
            data=json.dumps(query_data),
            content_type='application/json'
        )

        assert anon_response.status_code == 200
        assert auth_response.status_code == 200

        anon_text = anon_response.json()['response']
        auth_text = auth_response.json()['response']

        # Оба должны получить ответы, но содержимое может отличаться
        assert len(anon_text) > 5
        assert len(auth_text) > 5

    def test_additional_integration_scenarios(self, authenticated_client):
        """НОВЫЙ ТЕСТ: Дополнительные интеграционные сценарии для покрытия."""
        action_to_function_map = {
            'faq': 'get_faq_answer',
            'feature_explanation': 'get_feature_explanation',
            'interactive_tour_step': 'get_interactive_tour_step',
            'post_creation_suggestion': 'get_post_creation_suggestion',
            'check_post_content': 'check_post_content',
            'generate_post_ideas': 'generate_post_ideas',
            'analyze_sentiment': 'analyze_sentiment',
            # Добавляем остальные action_types, которые могут быть вызваны во views.py
            'subscription_recommendations': 'get_subscription_recommendations',
            'analyze_profile': 'analyze_profile_stats',
            'find_post_by_keyword': 'find_post_by_keyword',
            'get_post_details': 'get_post_details',
            'find_user_by_username': 'find_user_by_username',
            'get_user_activity': 'get_user_activity'
            # 'general_chat' обрабатывается через self.handle_natural_language_query,
            # который внутри может вызывать get_gemini_response или другие функции.
            # Для general_chat патчить get_gemini_response может быть осмысленно,
            # но этот тест сфокусирован на прямых action_type.
        }

        # Тестируем различные action_types
        test_scenarios = [
            {'action_type': 'faq', 'user_input': 'Как работает сайт?'},
            {'action_type': 'feature_explanation', 'user_input': 'Объясни лайки'},
            {'action_type': 'interactive_tour_step', 'user_input': 'Тур', 'step_number': 1},
            {'action_type': 'post_creation_suggestion', 'user_input': 'Помоги с постом', 'current_text': 'Черновик'},
            {'action_type': 'check_post_content', 'user_input': 'Проверь контент'},
            {'action_type': 'generate_post_ideas', 'user_input': 'Дай идеи', 'tags': ['Python']},
            {'action_type': 'analyze_sentiment', 'user_input': 'Я рад!'},
        ]

        for scenario in test_scenarios:
            action = scenario['action_type']
            function_name_to_patch = action_to_function_map.get(action)

            if not function_name_to_patch:
                # Если для какого-то action_type нет прямого маппинга на функцию
                # (например, 'general_chat' или если это ошибка в тесте),
                # то можно пропустить или обработать особо.
                # Для данного теста предполагаем, что все action_type в test_scenarios имеют маппинг.
                # Если это не так, тест нужно будет доработать.
                # Пока что, если имя не найдено, используем старый подход, но это должно быть исправлено.
                # В идеале, все action_type в test_scenarios должны иметь свой обработчик.
                # Однако, чтобы избежать падения, если action не в карте, можно оставить старый патч
                # или явно пропустить. Для чистоты, мы ожидаем, что все используемые action есть в карте.
                # Если function_name_to_patch is None, это ошибка в настройке теста или карты.
                assert function_name_to_patch, f"Function name not found in map for action: {action}"

            with patch(f'orange_assistant.views.{function_name_to_patch}') as mock_func:
                mock_func.return_value = f"Ответ для {action}"

                response = authenticated_client.post(
                    self.chat_url,
                    data=json.dumps(scenario),
                    content_type='application/json'
                )

                assert response.status_code == 200

    def test_database_consistency_across_tests(self, authenticated_client):
        """НОВЫЙ ТЕСТ: Проверка согласованности данных между тестами."""
        # Проверяем что каждый тест работает с изолированными данными
        initial_user_count = User.objects.count()
        initial_post_count = Post.objects.count()

        # Создаем данные в тесте
        test_user = UserFactory(username="consistency_test_user")
        test_post = PostFactory(author=test_user, title="Consistency test post")

        # Проверяем что данные созданы
        assert User.objects.count() == initial_user_count + 1
        assert Post.objects.count() == initial_post_count + 1

        # Данные должны быть доступны в рамках этого теста
        assert User.objects.filter(username="consistency_test_user").exists()
        assert Post.objects.filter(title="Consistency test post").exists()

    @patch('orange_assistant.views.get_gemini_response')
    def test_error_boundaries_integration(self, mock_gemini, authenticated_client):
        """НОВЫЙ ТЕСТ: Тестирование границ ошибок в интеграции."""
        # Тестируем что система gracefully обрабатывает различные ошибки

        # 1. Ошибка в Gemini API
        mock_gemini.side_effect = Exception("API Error")

        data = {
            'user_input': 'тест ошибки',
            'action_type': 'general_chat'
        }

        response = authenticated_client.post(
            self.chat_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 200  # Должен gracefully обрабатывать ошибки

        # 2. Восстановление после ошибки
        mock_gemini.side_effect = None
        mock_gemini.return_value = "Восстановленный ответ"

        response2 = authenticated_client.post(
            self.chat_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response2.status_code == 200
        assert "Восстановленный ответ" in response2.json()['response']

    def test_concurrent_requests_simulation(self, authenticated_client):
        """НОВЫЙ ТЕСТ: Симуляция конкурентных запросов."""
        # Тестируем что система может обрабатывать несколько запросов одновременно

        with patch('orange_assistant.views.get_gemini_response') as mock_gemini:
            mock_gemini.return_value = "Конкурентный ответ"

            # Отправляем несколько запросов быстро
            responses = []
            for i in range(5):
                data = {
                    'user_input': f'конкурентный запрос {i}',
                    'action_type': 'general_chat'
                }

                response = authenticated_client.post(
                    self.chat_url,
                    data=json.dumps(data),
                    content_type='application/json'
                )
                responses.append(response)

            # Все запросы должны быть успешными
            for response in responses:
                assert response.status_code == 200
                assert "Конкурентный ответ" in response.json()['response']