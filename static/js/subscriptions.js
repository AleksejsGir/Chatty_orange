document.addEventListener('DOMContentLoaded', function() {
    console.log('Subscription script loaded!');

    document.querySelectorAll('.js-subscription-toggle').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            console.log('Subscription button clicked:', this);

            const username = this.dataset.username;

            if (!username) {
                console.error('Could not determine username for subscription toggle, data-username attribute is missing.');
                return;
            }

            console.log('Processing subscription for username:', username);

            // Сохраняем оригинальное состояние кнопки
            const originalHTML = this.innerHTML;
            const originalDisabled = this.disabled;

            // Показываем загрузку
            this.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
            this.disabled = true;

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
                this.innerHTML = originalHTML;
                this.disabled = originalDisabled;
                alert('Произошла ошибка при обработке запроса: ' + error.message);
            });
        });
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