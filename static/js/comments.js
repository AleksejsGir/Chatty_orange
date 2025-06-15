// comments.js - Обработчики для действий с комментариями
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация tooltips
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
            const repliesBlock = commentBlock.querySelector('.replies');

            // Проверяем, открыты ли уже ответы
            const isExpanded = repliesBlock && !repliesBlock.classList.contains('d-none');

            // Закрываем все другие открытые ответы и формы
            document.querySelectorAll('.replies').forEach(replies => {
                replies.classList.add('d-none');
            });
            document.querySelectorAll('.reply-form').forEach(form => {
                form.remove();
            });

            // Переключаем состояние текущего блока ответов
            if (repliesBlock) {
                if (isExpanded) {
                    repliesBlock.classList.add('d-none');
                } else {
                    repliesBlock.classList.remove('d-none');
                }
            }

            // Обработка формы ответа
            if (isExpanded) {
                // Если ответы уже открыты - удаляем форму
                const existingForm = repliesContainer.querySelector('.reply-form');
                if (existingForm) existingForm.remove();
            } else {
                // Создаем новую форму ответа
                const parentId = this.dataset.commentId;
                const replyForm = document.createElement('div');
                replyForm.className = 'reply-form mt-3';
                const csrfToken = getCookie('csrftoken');
                replyForm.innerHTML = `
                    <form method="post" action="/posts/comments/${parentId}/reply/" class="mt-2">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                        <textarea name="text" class="form-control reply-textarea" rows="2" placeholder="Напишите ответ..." style="resize: vertical;" required></textarea>
                        <div class="mt-2 d-flex gap-2">
                            <button type="submit" class="btn btn-primary btn-sm">Отправить</button>
                            <button type="button" class="btn btn-outline-secondary btn-sm cancel-reply">Отмена</button>
                        </div>
                    </form>
                `;

                repliesContainer.appendChild(replyForm);

                // Прокручиваем к форме ответа
                replyForm.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

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
                    const form = this;
                    const formData = new FormData(form);

                    // Показываем индикатор загрузки
                    const submitBtn = form.querySelector('button[type="submit"]');
                    const originalText = submitBtn.textContent;
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Отправка...';

                    fetch(form.action, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.success) {
                            const newComment = document.createElement('div');
                            newComment.innerHTML = data.html;

                            // Находим контейнер для ответов
                            let repliesBlock = commentBlock.querySelector('.replies');
                            if (!repliesBlock) {
                                repliesBlock = document.createElement('div');
                                repliesBlock.className = 'replies mt-3';
                                commentBlock.appendChild(repliesBlock);
                            }

                            // Убираем скрытие ответов
                            repliesBlock.classList.remove('d-none');

                            // Вставляем новый комментарий
                            repliesBlock.prepend(newComment.firstElementChild);

                            // Удаляем форму
                            replyForm.remove();

                            // Обновляем счетчик ответов
                            const replyButton = commentBlock.querySelector('.btn-reply');
                            if (replyButton) {
                                const countBadge = replyButton.querySelector('.badge') || document.createElement('span');
                                if (!replyButton.querySelector('.badge')) {
                                    countBadge.className = 'badge bg-secondary ms-1';
                                    replyButton.appendChild(countBadge);
                                }

                                // Получаем текущее количество ответов
                                let currentCount = parseInt(countBadge.textContent) || 0;
                                countBadge.textContent = currentCount + 1;
                            }

                            // Анимация появления
                            newComment.firstElementChild.style.opacity = 0;
                            newComment.firstElementChild.style.transform = 'translateY(20px)';
                            setTimeout(() => {
                                newComment.firstElementChild.style.transition = 'opacity 0.3s, transform 0.3s';
                                newComment.firstElementChild.style.opacity = 1;
                                newComment.firstElementChild.style.transform = 'translateY(0)';
                            }, 10);
                        } else {
                            alert(`Ошибка: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        console.error('Error submitting reply:', error);
                        alert('Произошла ошибка при отправке комментария');
                    })
                    .finally(() => {
                        submitBtn.disabled = false;
                        submitBtn.textContent = originalText;
                    });
                });

                // Обработчик кнопки "Отмена"
                replyForm.querySelector('.cancel-reply').addEventListener('click', function() {
                    replyForm.remove();
                });
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

// Функция переключения реакции
function toggleReaction(commentId, emoji) {
    fetch(`/posts/comments/${commentId}/toggle-reaction/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: `emoji=${encodeURIComponent(emoji)}`
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            updateReactionUI(commentId, data.reactions, data.user_reactions);
        } else {
            console.error('Error:', data.message);
        }
    })
    .catch(error => console.error('Error toggling reaction:', error));
}

// Обновление UI после изменения реакции
function updateReactionUI(commentId, reactions, userReactions) {
    const container = document.querySelector(`.comment-block[data-comment-id="${commentId}"] .reactions-summary`);
    if (!container) return;

    // Очищаем текущие реакции
    container.innerHTML = '';

    // Создаем словарь для группировки реакций
    const groupedReactions = {};

    // Группируем реакции по emoji
    reactions.forEach(reaction => {
        if (!groupedReactions[reaction.emoji]) {
            groupedReactions[reaction.emoji] = {
                count: 0,
                emoji: reaction.emoji
            };
        }
        groupedReactions[reaction.emoji].count += reaction.count;
    });

    // Добавляем обновленные реакции
    Object.values(groupedReactions).forEach(reaction => {
        if (reaction.count > 0) {
            const badge = document.createElement('span');
            badge.className = 'badge reaction-badge me-1';

            // Добавляем класс user-reaction, если пользователь поставил эту реакцию
            if (userReactions.includes(reaction.emoji)) {
                badge.classList.add('user-reaction');
            }

            badge.dataset.emoji = reaction.emoji;
            badge.dataset.commentId = commentId;
            badge.textContent = `${reaction.emoji} ${reaction.count}`;

            // Добавляем обработчик
            badge.addEventListener('click', function() {
                toggleReaction(commentId, reaction.emoji);
            });

            container.appendChild(badge);
        }
    });
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