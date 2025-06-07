// comments.js - Обработчики для действий с комментариями
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {trigger: 'hover'});
    });
    // Обработчик удаления комментария
    document.querySelectorAll('.btn-delete-comment').forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            if (confirm('Удалить этот комментарий?')) {
                deleteComment(commentId);
            }
        });
    });

    // Обработчик редактирования комментария
    document.querySelectorAll('.btn-edit-comment').forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            toggleEditForm(commentId);
        });
    });

    // Обработчик ответа на комментарий
    document.querySelectorAll('.btn-reply-comment').forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            toggleReplyForm(commentId);
        });
    });

    // Обработчик реакции
    document.querySelectorAll('.btn-reaction').forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            addReaction(commentId, '👍'); // Пока используем 👍 как пример
        });
    });

    // Обработчик отправки формы редактирования
    document.querySelectorAll('.edit-comment-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const commentId = this.dataset.commentId;
            updateComment(commentId, this);
        });
    });

    // Обработчик отмены редактирования
    document.querySelectorAll('.cancel-edit').forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('.edit-comment-form');
            if (form) {
                const commentId = form.dataset.commentId;
                toggleEditForm(commentId);
            }
        });
    });

    // Обработчик отмены ответа
    document.querySelectorAll('.cancel-reply').forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('.reply-form');
            if (form) {
                const commentId = form.dataset.commentId;
                toggleReplyForm(commentId);
            }
        });
    });
});

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

// Функция добавления реакции
function addReaction(commentId, emoji) {
    const container = document.querySelector(`.reactions-container[data-comment-id="${commentId}"]`);
    let badge = container.querySelector(`.reaction-badge[data-emoji="${emoji}"]`);

    if (badge) {
        const countElement = badge.querySelector('.count');
        countElement.textContent = parseInt(countElement.textContent) + 1;
    } else {
        container.innerHTML += `
            <span class="reaction-badge" data-emoji="${emoji}">
                ${emoji} <span class="count">1</span>
            </span>
        `;
    }

    // Здесь будет вызов на сервер для сохранения реакции
    console.log(`Added ${emoji} to comment ${commentId}`);
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