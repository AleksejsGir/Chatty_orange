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
            const repliesContainer = commentBlock.querySelector('.replies-container');

            // Закрываем все другие открытые формы ответа
            document.querySelectorAll('.reply-form').forEach(form => {
                if (!form.closest('.comment-block').isSameNode(commentBlock)) {
                    form.classList.add('d-none');
                }
            });

            // Проверяем, есть ли уже открытая форма в этом контейнере
            let existingForm = repliesContainer.querySelector('.reply-form:not(.d-none)');
            if (existingForm) {
                existingForm.classList.add('d-none');
            }

            // Создаём новую форму ответа
            const parentId = this.dataset.commentId;
            const replyForm = document.createElement('div');
            replyForm.className = 'reply-form d-none mt-3';
            const csrfToken = getCookie('csrftoken');
            replyForm.innerHTML = `
            <form method="post" action="/comments/${parentId}/reply/" class="mt-2">
                <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                <textarea name="text" class="form-control reply-textarea" rows="1" placeholder="Напишите ответ..." style="resize: vertical;"></textarea>
                <div class="mt-2">
                    <button type="submit" class="btn btn-primary btn-sm">Сохранить</button>
                    <button type="button" class="btn btn-secondary btn-sm cancel-reply">Отмена</button>
                </div>
            </form>
        `;

            repliesContainer.appendChild(replyForm);
            replyForm.classList.remove('d-none');

            // Динамическое расширение textarea
            const textarea = replyForm.querySelector('.reply-textarea');
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });

            // Фокусируемся на поле ввода
            textarea.focus();

            // Обработчик отправки формы
            replyForm.querySelector('form').addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(this);
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
                            const newComment = document.createElement('div');
                            newComment.innerHTML = data.html;
                            const replies = commentBlock.querySelector('.replies');
                            if (!replies) {
                                const repliesDiv = document.createElement('div');
                                repliesDiv.className = 'replies mt-3';
                                commentBlock.appendChild(repliesDiv);
                                repliesDiv.appendChild(newComment.firstChild);
                            } else {
                                replies.appendChild(newComment.firstChild);
                            }
                            replyForm.remove();
                            commentBlock.style.minHeight = (commentBlock.scrollHeight + 100) + 'px';
                        } else {
                            console.error('Error adding reply:', data.error);
                        }
                    })
                    .catch(error => console.error('Error submitting reply:', error));
            });

            // Обработчик кнопки "Отмена"
            replyForm.querySelector('.cancel-reply').addEventListener('click', function() {
                replyForm.remove();
            });
        });
    });

    // Обработчик кнопки отмены ответа
    document.querySelectorAll('.cancel-reply').forEach(button => {
        button.addEventListener('click', function() {
            const replyForm = this.closest('.reply-form');
            if (replyForm) {
                replyForm.remove();
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
    fetch(`/comments/${commentId}/react/`, {
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