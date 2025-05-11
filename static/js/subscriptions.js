document.addEventListener('DOMContentLoaded', function() {
    // Находим все кнопки подписки/отписки на странице
    const subscriptionButtons = document.querySelectorAll('.subscription-toggle');

    // Для каждой кнопки добавляем обработчик события клика
    subscriptionButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();

            // Получаем имя пользователя из атрибута data-username
            const username = this.dataset.username;

            // Формируем URL для запроса
            const url = `/subscriptions/toggle/${username}/`;

            // Получаем CSRF токен для запроса
            const csrftoken = getCookie('csrftoken');

            // Отображаем состояние загрузки
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
            this.disabled = true;

            // Отправляем AJAX запрос
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка сети или сервера');
                }
                return response.json();
            })
            .then(data => {
                // Обновляем текст и стиль кнопки в зависимости от результата
                if (data.is_subscribed) {
                    button.innerHTML = '<i class="fa-solid fa-user-minus me-1"></i>Отписаться';
                    button.classList.remove('btn-primary', 'btn-follow-profile');
                    button.classList.add('btn-outline-secondary');
                } else {
                    button.innerHTML = '<i class="fa-solid fa-user-plus me-1"></i>Подписаться';
                    button.classList.remove('btn-outline-secondary');
                    button.classList.add('btn-primary', 'btn-follow-profile');
                }

                // Разблокируем кнопку
                button.disabled = false;

                // Обновляем счетчик подписчиков, если он есть на странице
                const subscribersCounter = document.getElementById('subscribers-count');
                if (subscribersCounter) {
                    subscribersCounter.textContent = data.subscribers_count;
                }

                // Отображаем сообщение об успешной подписке/отписке
                showNotification(data.message, 'success');
            })
            .catch(error => {
                console.error('Ошибка:', error);
                // Восстанавливаем исходное состояние кнопки
                button.innerHTML = originalText;
                button.disabled = false;
                showNotification('Произошла ошибка при обработке запроса', 'danger');
            });
        });
    });

    // Функция для отображения уведомления
    function showNotification(message, type = 'success') {
        // Создаем элемент уведомления
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} subscription-notification`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '1050';
        notification.style.maxWidth = '300px';
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-20px)';
        notification.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        notification.innerHTML = message;

        // Добавляем уведомление на страницу
        document.body.appendChild(notification);

        // Запускаем анимацию появления
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 10);

        // Удаляем уведомление через 3 секунды
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';

            // Полностью удаляем элемент после завершения анимации
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // Функция для получения CSRF токена из cookies
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
});