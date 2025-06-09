// comments.js - Обработчики для действий с комментариями
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {trigger: 'hover'});
    });

    // Обработчик кнопки "Ответить"
    document.querySelectorAll('.btn-reply').forEach(button => {
        button.addEventListener('click', function() {
            const commentBlock = this.closest('.comment-block');
            const commentId = commentBlock.dataset.commentId;
            const replyForm = commentBlock.querySelector('.reply-form');

            if (replyForm) {
                replyForm.classList.toggle('d-none');
            }
        });
    });

    // Обработчик кнопки отмены ответа
    document.querySelectorAll('.cancel-reply').forEach(button => {
        button.addEventListener('click', function() {
            const replyForm = this.closest('.reply-form');
            if (replyForm) {
                replyForm.classList.add('d-none');
            }
        });
    });

    // Обработчики для кнопок быстрых реакций
    document.querySelectorAll('.btn-reaction-quick').forEach(button => {
        button.addEventListener('click', function() {
            const emoji = this.dataset.emoji;
            const commentBlock = this.closest('.comment-block');
            const commentId = commentBlock.dataset.commentId;
            toggleReaction(commentId, emoji);
        });
    });

    // Обработчики для существующих реакций
    document.querySelectorAll('.reaction-badge').forEach(badge => {
        badge.addEventListener('click', function() {
            const emoji = this.dataset.emoji;
            const commentId = this.dataset.commentId;
            toggleReaction(commentId, emoji);
        });
    });

    // Обработчик реакции (кнопка смайлика)
    document.querySelectorAll('.btn-action.text-muted').forEach(button => {
        button.addEventListener('click', function() {
            if (this.getAttribute('title') === 'Реакция') {
                const commentBlock = this.closest('.comment-block');
                const commentId = commentBlock.dataset.commentId;
                // Здесь будет логика для открытия выбора эмодзи
                // Пока просто пример: добавим реакцию "👍"
                toggleReaction(commentId, '👍');
            }
        });
    });

    // Обработчик эмодзи-пикера (если используется)
    const picker = document.querySelector('emoji-picker');
    if (picker) {
        picker.addEventListener('emoji-click', event => {
            const emoji = event.detail.unicode;
            const activeComment = document.querySelector('.comment-block:hover');

            if (activeComment) {
                const commentId = activeComment.dataset.commentId;
                toggleReaction(commentId, emoji);
            }
        });
    }

    // Обработчик удаления комментария
    document.querySelectorAll('.btn-action.text-danger').forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Удалить этот комментарий?')) {
                e.preventDefault();
            }
        });
    });
});

// Функция переключения реакции (добавить/удалить)
function toggleReaction(commentId, emoji) {
    // Отправляем запрос на сервер
    fetch(`/posts/comment/${commentId}/toggle-reaction/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ emoji: emoji })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateReactionUI(commentId, emoji, data.action);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Обновление UI после изменения реакции
function updateReactionUI(commentId, emoji, action) {
    const container = document.querySelector(`.comment-block[data-comment-id="${commentId}"] .emoji-reactions`);
    if (!container) return;

    // Поиск существующей реакции
    let badge = container.querySelector(`.reaction-badge[data-emoji="${emoji}"]`);

    if (action === 'added') {
        if (badge) {
            // Увеличиваем счетчик
            const count = parseInt(badge.textContent.match(/\d+/)[0]) + 1;
            badge.textContent = `${emoji} ${count}`;
            badge.classList.add('user-reaction', 'added');

            // Анимация
            setTimeout(() => badge.classList.remove('added'), 300);
        } else {
            // Создаем новый бейдж
            const newBadge = document.createElement('span');
            newBadge.className = 'badge reaction-badge me-1 user-reaction added';
            newBadge.dataset.emoji = emoji;
            newBadge.dataset.commentId = commentId;
            newBadge.textContent = `${emoji} 1`;
            container.prepend(newBadge);

            // Добавляем обработчик
            newBadge.addEventListener('click', function() {
                toggleReaction(commentId, emoji);
            });

            // Анимация
            setTimeout(() => newBadge.classList.remove('added'), 300);
        }
    } else if (action === 'removed' && badge) {
        // Уменьшаем счетчик или удаляем
        const count = parseInt(badge.textContent.match(/\d+/)[0]) - 1;

        if (count > 0) {
            badge.textContent = `${emoji} ${count}`;
            badge.classList.remove('user-reaction');
        } else {
            badge.remove();
        }
    }

    // Удаляем реакцию пользователя из других эмодзи
    container.querySelectorAll('.reaction-badge.user-reaction').forEach(b => {
        if (b.dataset.emoji !== emoji) {
            b.classList.remove('user-reaction');
        }
    });
}

// Функция удаления комментария через AJAX
function deleteComment(commentId) {
    const url = `/posts/comment/${commentId}/delete/`;
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

    fetch(url, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const commentElement = document.querySelector(`.comment-block[data-comment-id="${commentId}"]`);
            if (commentElement) {
                commentElement.remove();
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

// Функция обновления комментария
function updateComment(commentId, formElement) {
    const formData = new FormData(formElement);

    fetch(`/posts/comment/${commentId}/update/`, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const content = document.querySelector(`.comment-content[data-comment-id="${commentId}"] p`);
            if (content) {
                content.textContent = data.new_text;
            }
            toggleEditForm(commentId);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Функция переключения формы редактирования
function toggleEditForm(commentId) {
    const container = document.querySelector(`.edit-form-container[data-comment-id="${commentId}"]`);
    const content = document.querySelector(`.comment-content[data-comment-id="${commentId}"]`);

    if (container && content) {
        container.classList.toggle('active');
        content.style.display = content.style.display === 'none' ? 'block' : 'none';

        // Автофокус на текстовом поле
        if (container.classList.contains('active')) {
            const textarea = container.querySelector('textarea');
            if (textarea) {
                textarea.focus();
                textarea.setSelectionRange(textarea.value.length, textarea.value.length);
            }
        }
    }
}

// Функция переключения формы ответа
function toggleReplyForm(commentId) {
    const container = document.querySelector(`.reply-form[data-comment-id="${commentId}"]`);
    if (container) {
        container.classList.toggle('active');
    }
}

// Функция для получения CSRF токена
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

// Обработчик кнопки "Редактировать"
document.querySelectorAll('.btn-edit-comment').forEach(btn => {
    btn.addEventListener('click', function() {
        const commentBlock = this.closest('.comment-block');
        const commentId = commentBlock.dataset.commentId;

        // Скрываем основной контент
        commentBlock.querySelector('.comment-content').classList.add('d-none');

        // Показываем форму редактирования
        commentBlock.querySelector('.edit-form').classList.remove('d-none');
    });
});

// Обработчик отмены редактирования
document.querySelectorAll('.cancel-edit').forEach(btn => {
    btn.addEventListener('click', function() {
        const form = this.closest('.edit-form');
        const commentBlock = form.closest('.comment-block');

        // Показываем основной контент
        commentBlock.querySelector('.comment-content').classList.remove('d-none');

        // Скрываем форму
        form.classList.add('d-none');
    });
});

// Обработчик отправки формы редактирования
document.querySelectorAll('.edit-comment-form').forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const commentId = this.dataset.commentId;

        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Обновляем текст комментария
                const contentBlock = document.querySelector(
                    `.comment-block[data-comment-id="${commentId}"] .comment-content p`
                );
                contentBlock.textContent = data.new_text;

                // Восстанавливаем оригинальный вид
                this.closest('.edit-form').classList.add('d-none');
                contentBlock.parentElement.classList.remove('d-none');
            }
        });
    });
});