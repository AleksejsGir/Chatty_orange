// static/js/likes.js - ИСПРАВЛЕННАЯ ВЕРСИЯ с полной CSRF защитой
document.addEventListener('DOMContentLoaded', function() {

    // ✅ ЕДИНАЯ функция для получения CSRF токена
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

    // ✅ ЕДИНЫЙ обработчик для лайков и дизлайков
    function handleReaction(button) {
        // Предотвращаем множественные клики
        if (button.disabled) return;

        const postId = button.dataset.postId;
        const isLike = button.classList.contains('like-button');
        const url = isLike ? `/posts/${postId}/like/` : `/posts/${postId}/dislike/`;

        // Временно отключаем кнопку
        button.disabled = true;

        fetch(url, {
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
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return response.json();
        })
        .then(data => {
            if (data.status === 'ok') {
                updateReactionButtons(postId, data);
            } else {
                console.error('Unexpected response:', data);
                showErrorMessage('Произошла ошибка при обработке реакции');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (error.message !== 'Unauthorized') {
                showErrorMessage('Ошибка сети. Попробуйте еще раз.');
            }
        })
        .finally(() => {
            // Включаем кнопку обратно
            button.disabled = false;
        });
    }

    // ✅ УЛУЧШЕННАЯ функция обновления состояния кнопок
    function updateReactionButtons(postId, data) {
        const likeButton = document.querySelector(`.like-button[data-post-id="${postId}"]`);
        const dislikeButton = document.querySelector(`.dislike-button[data-post-id="${postId}"]`);

        if (!likeButton || !dislikeButton) {
            console.error('Кнопки лайк/дизлайк не найдены для поста', postId);
            return;
        }

        // Обновляем состояние кнопки лайка
        likeButton.classList.toggle('active', data.liked || false);
        const likeIcon = likeButton.querySelector('i');
        if (likeIcon) {
            likeIcon.className = `fa-thumbs-up ${data.liked ? 'fa-solid' : 'fa-regular'}`;
        }
        const likeCount = likeButton.querySelector('.interaction-count');
        if (likeCount) {
            likeCount.textContent = data.total_likes || 0;
        }

        // Обновляем состояние кнопки дизлайка
        dislikeButton.classList.toggle('active', data.disliked || false);
        const dislikeIcon = dislikeButton.querySelector('i');
        if (dislikeIcon) {
            dislikeIcon.className = `fa-thumbs-down ${data.disliked ? 'fa-solid' : 'fa-regular'}`;
        }
        const dislikeCount = dislikeButton.querySelector('.interaction-count');
        if (dislikeCount) {
            dislikeCount.textContent = data.total_dislikes || 0;
        }

        // ✅ Анимация при изменении (если доступен GSAP)
        if (typeof gsap !== 'undefined') {
            const changedButton = data.liked ? likeButton : (data.disliked ? dislikeButton : null);
            if (changedButton) {
                gsap.fromTo(changedButton,
                    { scale: 1 },
                    { scale: 1.1, duration: 0.1, yoyo: true, repeat: 1 }
                );
            }
        }
    }

    // ✅ Уведомление для неавторизованных пользователей
    function showLoginAlert() {
        if (confirm('Для выполнения этого действия требуется войти в систему. Перейти на страницу входа?')) {
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

    // ✅ ЕДИНСТВЕННЫЙ обработчик событий
    document.addEventListener('click', function(event) {
        const button = event.target.closest('.like-button, .dislike-button');
        if (button) {
            event.preventDefault();
            handleReaction(button);
        }
    });

    // ✅ ДОПОЛНИТЕЛЬНО: Обработка клавиатуры для доступности
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            const button = event.target.closest('.like-button, .dislike-button');
            if (button) {
                event.preventDefault();
                handleReaction(button);
            }
        }
    });

    // ✅ Логирование для отладки (можно убрать в продакшне)
    console.log('Likes.js loaded successfully with CSRF protection');
});