// static/js/subscriptions.js - ИСПРАВЛЕННАЯ ВЕРСИЯ с полной CSRF защитой и улучшенным UX
document.addEventListener('DOMContentLoaded', function() {
    console.log('Subscription script loaded with CSRF protection!');

    // ✅ ЕДИНАЯ функция для получения CSRF токена (с fallback)
    function getCSRFToken() {
        // Сначала пробуем получить токен из meta тега
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }

        // Затем из скрытого поля формы
        const hiddenToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (hiddenToken) {
            return hiddenToken.value;
        }

        // В крайнем случае из cookie
        return getCookie('csrftoken');
    }

    // ✅ Базовая функция получения cookie (как fallback)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // ✅ БЕЗОПАСНЫЕ заголовки для всех запросов
    function createSecureHeaders() {
        const csrfToken = getCSRFToken();
        const headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        };

        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        } else {
            console.warn('CSRF токен не найден! Запрос может быть отклонен.');
        }

        return headers;
    }

    // ✅ УЛУЧШЕННАЯ функция обработки подписок
    function handleSubscriptionToggle(button) {
        // Предотвращаем множественные клики
        if (button.disabled) return;

        const username = button.dataset.username;
        if (!username) {
            console.error('Username не найден в data-username атрибуте');
            showErrorMessage('Ошибка: не удалось определить пользователя');
            return;
        }

        console.log('Processing subscription for username:', username);

        // Сохраняем оригинальное состояние
        const originalHTML = button.innerHTML;
        const originalClasses = button.className;

        // Показываем загрузку
        button.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Обработка...';
        button.disabled = true;

        // Отправляем безопасный запрос
        fetch(`/subscriptions/toggle/${username}/`, {
            method: 'POST',
            headers: createSecureHeaders(), // ✅ CSRF защита включена!
            credentials: 'same-origin'
        })
        .then(response => {
            if (response.status === 401 || response.status === 403) {
                showLoginAlert();
                throw new Error('Unauthorized');
            }

            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }

            return response.json();
        })
        .then(data => {
            console.log('Server response:', data);

            if (data.status === 'success') {
                // ✅ ДИНАМИЧЕСКОЕ обновление вместо перезагрузки страницы
                updateSubscriptionButton(button, data);
                showSuccessMessage(data.message || 'Действие выполнено успешно!');
            } else {
                throw new Error(data.message || 'Неожиданный ответ сервера');
            }
        })
        .catch(error => {
            console.error('Error toggling subscription:', error);

            // Восстанавливаем оригинальное состояние при ошибке
            button.innerHTML = originalHTML;
            button.className = originalClasses;

            if (error.message !== 'Unauthorized') {
                showErrorMessage('Ошибка: ' + error.message);
            }
        })
        .finally(() => {
            // Включаем кнопку обратно
            button.disabled = false;
        });
    }

    // ✅ ДИНАМИЧЕСКОЕ обновление кнопки без перезагрузки страницы
    function updateSubscriptionButton(button, data) {
        const isSubscribed = data.subscribed;

        // Обновляем текст и класс кнопки
        if (isSubscribed) {
            button.innerHTML = '<i class="fa-solid fa-user-minus me-1"></i>Отписаться';
            button.className = 'btn btn-outline-danger btn-sm js-subscription-toggle';
        } else {
            button.innerHTML = '<i class="fa-solid fa-user-plus me-1"></i>Подписаться';
            button.className = 'btn btn-primary btn-sm js-subscription-toggle';
        }

        // ✅ Анимация изменения (если доступен GSAP)
        if (typeof gsap !== 'undefined') {
            gsap.fromTo(button,
                { scale: 1 },
                { scale: 1.05, duration: 0.15, yoyo: true, repeat: 1 }
            );
        }

        // ✅ Обновляем счетчики подписчиков, если есть на странице
        updateSubscriberCounts(data);
    }

    // ✅ Обновление счетчиков подписчиков на странице
    function updateSubscriberCounts(data) {
        // Ищем элементы со счетчиками подписчиков
        const subscribersCountElements = document.querySelectorAll('.subscribers-count, [data-subscribers-count]');

        if (data.subscribers_count !== undefined) {
            subscribersCountElements.forEach(element => {
                element.textContent = data.subscribers_count;
            });
        }

        // Можно также обновить счетчик в навигации или других местах
        const profileStatsElement = document.querySelector('.profile-subscribers-count');
        if (profileStatsElement && data.subscribers_count !== undefined) {
            profileStatsElement.textContent = `Подписчиков: ${data.subscribers_count}`;
        }
    }

    // ✅ Уведомление для неавторизованных пользователей
    function showLoginAlert() {
        if (confirm('Для подписки требуется войти в систему. Перейти на страницу входа?')) {
            window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
        }
    }

    // ✅ Показ ошибок пользователю
    function showErrorMessage(message) {
        // Можно заменить на более красивое уведомление (toast, modal и т.д.)
        alert(message);

        // Или использовать Bootstrap toast, если доступен:
        /*
        const toastHTML = `
            <div class="toast align-items-center text-white bg-danger border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        // Добавить в контейнер и показать
        */
    }

    // ✅ Показ успешных уведомлений
    function showSuccessMessage(message) {
        // Временное решение - можно заменить на toast
        console.log('Success:', message);

        // Или показать ненавязчивое уведомление
        /*
        const toastHTML = `
            <div class="toast align-items-center text-white bg-success border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        */
    }

    // ✅ ЕДИНЫЙ обработчик событий (Event Delegation)
    document.addEventListener('click', function(event) {
        const button = event.target.closest('.js-subscription-toggle');
        if (button) {
            event.preventDefault();
            handleSubscriptionToggle(button);
        }
    });

    // ✅ ДОПОЛНИТЕЛЬНО: Обработка клавиатуры для доступности
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            const button = event.target.closest('.js-subscription-toggle');
            if (button) {
                event.preventDefault();
                handleSubscriptionToggle(button);
            }
        }
    });

    // ✅ Дополнительная функция: массовые операции подписки
    function handleBulkSubscriptions(usernames, action) {
        if (!Array.isArray(usernames) || usernames.length === 0) {
            showErrorMessage('Не выбраны пользователи для действия');
            return;
        }

        const promises = usernames.map(username =>
            fetch(`/subscriptions/toggle/${username}/`, {
                method: 'POST',
                headers: createSecureHeaders(),
                credentials: 'same-origin'
            }).then(response => response.json())
        );

        Promise.all(promises)
            .then(results => {
                const successful = results.filter(r => r.status === 'success').length;
                showSuccessMessage(`Успешно обработано: ${successful} из ${usernames.length}`);

                // Обновляем UI для всех обработанных пользователей
                results.forEach((result, index) => {
                    if (result.status === 'success') {
                        const button = document.querySelector(`[data-username="${usernames[index]}"]`);
                        if (button) updateSubscriptionButton(button, result);
                    }
                });
            })
            .catch(error => {
                showErrorMessage('Ошибка при массовой операции: ' + error.message);
            });
    }

    // ✅ Экспортируем функцию для использования в других скриптах
    window.handleBulkSubscriptions = handleBulkSubscriptions;

    // ✅ Логирование для отладки (можно убрать в продакшне)
    console.log('Subscriptions.js loaded successfully with CSRF protection');
});