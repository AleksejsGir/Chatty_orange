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

    // Обработчик реакции (кнопка смайлика)
    document.querySelectorAll('.btn-action.text-muted').forEach(button => {
        button.addEventListener('click', function() {
            if (this.getAttribute('title') === 'Реакция') {
                const commentBlock = this.closest('.comment-block');
                const commentId = commentBlock.dataset.commentId;
                // Здесь будет логика для открытия выбора эмодзи
                // Пока просто пример: добавим реакцию "👍"
                addReaction(commentId, '👍');
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
                addReaction(commentId, emoji);
            }
        });
    }

    // Обработчик удаления комментария (теперь кнопка удаления имеет классы 'btn-action text-danger')
    document.querySelectorAll('.btn-action.text-danger').forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Удалить этот комментарий?')) {
                e.preventDefault();
            }
        });
    });
});

// Функция добавления реакции (адаптирована под новую структуру)
function addReaction(commentId, emoji) {
    const container = document.querySelector(`.comment-block[data-comment-id="${commentId}"] .emoji-reactions`);
    if (!container) return;

    let badge = container.querySelector(`.reaction-badge[data-emoji="${emoji}"]`);

    if (badge) {
        const count = parseInt(badge.textContent.match(/\d+/)[0]) + 1;
        badge.textContent = `${emoji} ${count}`;
    } else {
        const newBadge = document.createElement('span');
        newBadge.className = 'badge reaction-badge me-1';
        newBadge.dataset.emoji = emoji;
        newBadge.dataset.commentId = commentId;
        newBadge.textContent = `${emoji} 1`;
        container.appendChild(newBadge);
    }

    // Здесь будет вызов на сервер для сохранения реакции
    console.log(`Added ${emoji} to comment ${commentId}`);
}

// Остальные функции (deleteComment, updateComment и т.д.) остаются без изменений

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