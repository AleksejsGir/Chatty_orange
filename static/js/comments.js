// comments.js - Обработчики для действий с комментариями
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {trigger: 'hover'});
    });

    // Обработчик кнопки "Реакция"
    document.querySelectorAll('.btn-reaction').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const container = this.closest('.reactions-container');
            if (container) {
                container.classList.toggle('active');
            }
        });
    });

    // Обработчик кнопки "Ответить"
    document.querySelectorAll('.btn-reply').forEach(button => {
        button.addEventListener('click', function() {
            const commentBlock = this.closest('.comment-block');
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
            const commentId = this.dataset.commentId;
            toggleReaction(commentId, emoji);

            // Закрываем панель после выбора
            const container = this.closest('.reactions-container');
            if (container) {
                container.classList.remove('active');
            }
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

    // Обработчик удаления комментария
    document.querySelectorAll('.btn-action.text-danger').forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Удалить этот комментарий?')) {
                e.preventDefault();
            }
        });
    });

    // Закрытие панели при клике вне её
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.reactions-container')) {
            document.querySelectorAll('.reactions-container').forEach(container => {
                container.classList.remove('active');
            });
        }
    });

    // Обработчик кнопки "Редактировать"
    document.querySelectorAll('.btn-edit-comment').forEach(btn => {
        btn.addEventListener('click', function() {
            const commentBlock = this.closest('.comment-block');
            commentBlock.querySelector('.comment-content').classList.add('d-none');
            commentBlock.querySelector('.edit-form').classList.remove('d-none');
        });
    });

    // Обработчик отмены редактирования
    document.querySelectorAll('.cancel-edit').forEach(btn => {
        btn.addEventListener('click', function() {
            const form = this.closest('.edit-form');
            const commentBlock = form.closest('.comment-block');
            commentBlock.querySelector('.comment-content').classList.remove('d-none');
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
                    const contentBlock = document.querySelector(
                        `.comment-block[data-comment-id="${commentId}"] .comment-content p`
                    );
                    contentBlock.textContent = data.new_text;
                    this.closest('.edit-form').classList.add('d-none');
                    contentBlock.parentElement.classList.remove('d-none');
                } else {
                    console.error('Error updating comment:', data.error);
                }
            })
            .catch(error => console.error('Error editing comment:', error));
        });
    });
});

// Функция переключения реакции (добавить/удалить)
function toggleReaction(commentId, emoji) {
    fetch(`/posts/comments/${commentId}/react/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ emoji: emoji })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            updateReactionUI(commentId, emoji, data.action, data.reactions);
        } else {
            console.error('Error:', data.message);
        }
    })
    .catch(error => console.error('Error toggling reaction:', error));
}

// Обновление UI после изменения реакции
function updateReactionUI(commentId, emoji, action, reactions) {
const container = document.querySelector(`.comment-block[data-comment-id="${commentId}"] .emoji-reactions`);
    if (!container) return;

    // Очищаем текущие реакции
    container.innerHTML = '';

    // Получаем список эмодзи, на которые пользователь уже отреагировал
    fetch(`/posts/comment/${commentId}/user-reactions/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.status === 401) {
            return []; // Пользователь не авторизован
        }
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(userReactions => {
        // Обновляем реакции на основе данных от сервера
        reactions.forEach(reaction => {
            if (reaction.count > 0) {
                const badge = document.createElement('span');
                badge.className = 'badge reaction-badge me-1';
                badge.dataset.emoji = reaction.emoji;
                badge.dataset.commentId = commentId;
                badge.textContent = `${reaction.emoji} ${reaction.count}`;

                // Добавляем класс user-reaction, если пользователь поставил эту реакцию
                if (userReactions.includes(reaction.emoji)) {
                    badge.classList.add('user-reaction');
                }

                // Анимация для добавленной реакции
                if (action === 'added' && reaction.emoji === emoji) {
                    badge.classList.add('added');
                    setTimeout(() => badge.classList.remove('added'), 300);
                }

                container.appendChild(badge);

                // Добавляем обработчик для новой реакции
                badge.addEventListener('click', function() {
                    toggleReaction(commentId, reaction.emoji);
                });
            }
        });
    })
    .catch(error => console.error('Error fetching user reactions:', error));
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