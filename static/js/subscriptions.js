document.addEventListener('DOMContentLoaded', function() {
    console.log('Subscription script loaded!');

    // Находим все элементы, с которыми можно работать
    const subscriptionButtons = document.querySelectorAll('.subscription-toggle, [data-username], .otpis-btn, button:contains("Отписаться")');
    console.log('Found subscription elements:', subscriptionButtons.length);

    // Обрабатываем клики на всем документе
    document.addEventListener('click', function(event) {
        // Если клик был на кнопку отписки/подписки или внутри неё
        if (event.target.closest('[data-username], .subscription-toggle, .otpis-btn') ||
            event.target.textContent.includes('Отписаться')) {

            const button = event.target.closest('button, [type="submit"]');
            if (!button) return;

            event.preventDefault();
            console.log('Subscription button clicked:', button);

            // Проверяем, есть ли у кнопки атрибут data-username
            let username = button.dataset.username;

            // Если нет, пытаемся найти его в ближайшей форме
            if (!username && button.form) {
                const formAction = button.form.action;
                // Попытка извлечь имя пользователя из URL формы
                const matches = formAction.match(/\/subscriptions\/toggle\/([^\/]+)\//);
                if (matches && matches[1]) {
                    username = matches[1];
                }
            }

            // Если всё еще нет, ищем в ближайших элементах с data-username
            if (!username) {
                const parentWithUsername = button.closest('[data-username]');
                if (parentWithUsername) {
                    username = parentWithUsername.dataset.username;
                }
            }

            if (!username) {
                console.error('Could not determine username for subscription toggle');
                return;
            }

            console.log('Processing subscription for username:', username);

            // Сохраняем оригинальное состояние кнопки
            const originalHTML = button.innerHTML;
            const originalDisabled = button.disabled;

            // Показываем загрузку
            button.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
            button.disabled = true;

            // Получаем CSRF токен
            const csrftoken = getCookie('csrftoken');

            // Отправляем запрос
            fetch(`/subscriptions/toggle/${username}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Server response:', data);
                // Перезагружаем страницу для гарантированного обновления
                window.location.reload();
            })
            .catch(error => {
                console.error('Error toggling subscription:', error);
                button.innerHTML = originalHTML;
                button.disabled = originalDisabled;
                alert('Произошла ошибка при обработке запроса: ' + error.message);
            });
        }
    });

    // Функция для получения CSRF-токена из куки
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