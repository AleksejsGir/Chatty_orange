# diagnostic_orange_assistant.py
# Запустите: python manage.py shell < diagnostic_orange_assistant.py

print("🔍 ДИАГНОСТИКА ORANGE ASSISTANT")
print("=" * 50)

# 1. Проверка доступа к базе данных
print("\n1. 📊 Проверка базы данных:")
try:
    from django.contrib.auth import get_user_model
    from posts.models import Post, Comment

    User = get_user_model()

    users_count = User.objects.count()
    posts_count = Post.objects.count()
    comments_count = Comment.objects.count()

    print(f"✅ Пользователей: {users_count}")
    print(f"✅ Постов: {posts_count}")
    print(f"✅ Комментариев: {comments_count}")

    # Проверяем конкретных пользователей
    print("\n📋 Существующие пользователи:")
    for user in User.objects.all()[:5]:
        print(f"   - @{user.username} (ID: {user.id})")

    # Проверяем посты
    print("\n📋 Существующие посты:")
    for post in Post.objects.all()[:5]:
        print(f"   - '{post.title}' от @{post.author.username}")

except Exception as e:
    print(f"❌ ОШИБКА доступа к БД: {e}")

# 2. Проверка функций ассистента
print("\n2. 🤖 Проверка функций ассистента:")
try:
    from orange_assistant.ai_services import find_user_by_username, get_subscription_recommendations

    test_user_info = {
        'username': 'test_user',
        'user_id': 1,
        'is_authenticated': True
    }

    # Тест поиска пользователя
    print("\n🔍 Тестирование поиска пользователя...")
    try:
        result = find_user_by_username("Orange", test_user_info)
        print(f"✅ Поиск 'Orange': {result[:100]}...")
    except Exception as e:
        print(f"❌ Ошибка поиска пользователя: {e}")

    # Тест поиска неправильным способом (как сейчас происходит)
    try:
        result = find_user_by_username("Найди пользователя Orange", test_user_info)
        print(f"❌ Неправильный поиск 'Найди пользователя Orange': {result[:100]}...")
    except Exception as e:
        print(f"❌ Ошибка неправильного поиска: {e}")

    # Тест рекомендаций
    print("\n📝 Тестирование рекомендаций...")
    try:
        result = get_subscription_recommendations(test_user_info)
        print(f"✅ Рекомендации: {result[:100]}...")
    except Exception as e:
        print(f"❌ Ошибка рекомендаций: {e}")

except ImportError as e:
    print(f"❌ ОШИБКА импорта: {e}")

# 3. Проверка views.py
print("\n3. 🔧 Проверка views.py:")
try:
    from orange_assistant.views import ChatWithAIView

    # Проверяем, есть ли у класса метод handle_natural_language_query
    if hasattr(ChatWithAIView, 'handle_natural_language_query'):
        print("✅ Метод handle_natural_language_query найден")

        # Пробуем вызвать метод напрямую
        view_instance = ChatWithAIView()
        test_result = view_instance.handle_natural_language_query(
            "Найди пользователя Orange",
            {'username': 'test'}
        )
        print(f"✅ Прямой вызов метода: {test_result[:100]}...")

    else:
        print("❌ Метод handle_natural_language_query НЕ НАЙДЕН!")
        print("   Нужно добавить метод в views.py")

except Exception as e:
    print(f"❌ ОШИБКА views.py: {e}")

# 4. Проверка API endpoint
print("\n4. 🌐 Проверка API:")
try:
    from django.test import Client
    from django.contrib.auth import get_user_model
    import json

    client = Client()

    # Тестируем API напрямую
    response = client.post('/assistant/api/chat/',
                           data=json.dumps({
                               'action_type': 'find_user_by_username',
                               'user_input': 'Orange',
                               'user_info': {'username': 'test'}
                           }),
                           content_type='application/json'
                           )

    print(f"📡 API статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API ответ: {data.get('response', '')[:100]}...")
    else:
        print(f"❌ API ошибка: {response.content}")

except Exception as e:
    print(f"❌ ОШИБКА API: {e}")

# 5. Создание тестовых данных
print("\n5. 🏗️ Создание тестовых данных:")
try:
    User = get_user_model()

    # Создаем пользователя Orange если его нет
    orange_user, created = User.objects.get_or_create(
        username='Orange',
        defaults={
            'email': 'orange@example.com',
            'first_name': 'Orange',
            'last_name': 'Assistant'
        }
    )

    if created:
        print("✅ Создан пользователь Orange")
    else:
        print(f"ℹ️ Пользователь Orange уже существует (ID: {orange_user.id})")

    # Создаем пользователя Alek если его нет
    alek_user, created = User.objects.get_or_create(
        username='Alek',
        defaults={
            'email': 'alek@example.com',
            'first_name': 'Alek',
            'last_name': 'User'
        }
    )

    if created:
        print("✅ Создан пользователь Alek")
    else:
        print(f"ℹ️ Пользователь Alek уже существует (ID: {alek_user.id})")

    # Создаем тестовые посты
    test_posts = [
        {
            'title': 'QLED телевизоры китайских производителей',
            'text': 'Обзор качественных QLED телевизоров от китайских производителей.',
            'author': orange_user
        },
        {
            'title': 'Путешествия по Европе',
            'text': 'Мой опыт путешествий по европейским столицам.',
            'author': alek_user
        }
    ]

    for post_data in test_posts:
        post, created = Post.objects.get_or_create(
            title=post_data['title'],
            defaults=post_data
        )
        if created:
            print(f"✅ Создан пост: {post.title}")

except Exception as e:
    print(f"❌ ОШИБКА создания данных: {e}")

print("\n🎯 ИТОГИ ДИАГНОСТИКИ:")
print("=" * 50)
print("Если видите ошибки выше, это источник проблемы!")
print("Основные причины:")
print("1. ❌ Метод handle_natural_language_query не обновлен в views.py")
print("2. ❌ Нет доступа к базе данных")
print("3. ❌ JavaScript отправляет неправильные данные")
print("4. ❌ Отсутствуют тестовые пользователи")