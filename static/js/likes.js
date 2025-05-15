// static/js/likes.js
document.addEventListener('DOMContentLoaded', function() {
    function handleReaction(button, url) {
        if (button.disabled) return;

        const postId = button.dataset.postId;
        const icon = button.querySelector('i');
        const count = button.querySelector('.interaction-count');
        const isLikeButton = button.classList.contains('like-button');

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (response.status === 403) {
                showLoginAlert();
                throw new Error('Unauthorized');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'ok') {
                // Обновляем текущую кнопку
                button.classList.toggle('active', isLikeButton ? data.liked : data.disliked);
                icon.classList.toggle('fa-regular', !(isLikeButton ? data.liked : data.disliked));
                icon.classList.toggle('fa-solid', isLikeButton ? data.liked : data.disliked);
                count.textContent = isLikeButton ? data.total_likes : data.total_dislikes;

                // Обновляем противоположную кнопку
                const oppositeButton = document.querySelector(
                    isLikeButton
                        ? `.dislike-button[data-post-id="${postId}"]`
                        : `.like-button[data-post-id="${postId}"]`
                );

                if (oppositeButton) {
                    oppositeButton.classList.remove('active');
                    const oppositeIcon = oppositeButton.querySelector('i');
                    oppositeIcon.classList.add('fa-regular');
                    oppositeIcon.classList.remove('fa-solid');
                    oppositeButton.querySelector('.interaction-count').textContent =
                        isLikeButton ? data.total_dislikes : data.total_likes;
                }
            }
        })
        .catch(error => console.error('Error:', error));
    }

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

// Обработчик дизлайков
document.querySelectorAll('.like-button, .dislike-button').forEach(button => {
    button.addEventListener('click', function() {
        const postId = this.dataset.postId;
        const isLike = this.classList.contains('like-button');
        const url = isLike ? `/posts/${postId}/like/` : `/posts/${postId}/dislike/`;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                // Обновляем обе кнопки и счетчики
                const likeButton = document.querySelector(`.like-button[data-post-id="${postId}"]`);
                const dislikeButton = document.querySelector(`.dislike-button[data-post-id="${postId}"]`);

                // Обновляем состояние кнопок
                likeButton.classList.toggle('active', data.liked);
                dislikeButton.classList.toggle('active', data.disliked);

                // Обновляем иконки
                likeButton.querySelector('i').className =
                    `fa-thumbs-up ${data.liked ? 'fa-solid text-primary' : 'fa-regular'}`;
                dislikeButton.querySelector('i').className =
                    `fa-thumbs-down ${data.disliked ? 'fa-solid text-primary' : 'fa-regular'}`;

                // Обновляем счетчики
                likeButton.querySelector('.interaction-count').textContent = data.total_likes;
                dislikeButton.querySelector('.interaction-count').textContent = data.total_dislikes;
            }
        });
    });
});

function showLoginAlert() {
    if(confirm('Для выполнения этого действия требуется войти в систему. Перейти на страницу входа?')) {
        window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
    }
}

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
    console.log('CSRF Token:', cookieValue); // Добавлено логирование
    return cookieValue;
}

function updateReactions(response, button) {
    // Для лайков
    if (button.classList.contains('like-button')) {
        const icon = button.querySelector('.fa-thumbs-up');
        icon.classList.toggle('fa-regular', !response.liked);
        icon.classList.toggle('fa-solid', response.liked);
        button.querySelector('.interaction-count').textContent = response.total_likes;

        if (response.removed_dislike) {
            const dislikeBtn = document.querySelector(`.dislike-button[data-post-id="${button.dataset.postId}"]`);
            dislikeBtn.querySelector('.fa-thumbs-down').classList.remove('fa-solid');
            dislikeBtn.querySelector('.interaction-count').textContent = response.total_dislikes;
        }
    }

    // Для дизлайков
    if (button.classList.contains('dislike-button')) {
        const icon = button.querySelector('.fa-thumbs-down');
        icon.classList.toggle('fa-regular', !response.disliked);
        icon.classList.toggle('fa-solid', response.disliked);
        button.querySelector('.interaction-count').textContent = response.total_dislikes;

        if (response.removed_like) {
            const likeBtn = document.querySelector(`.like-button[data-post-id="${button.dataset.postId}"]`);
            likeBtn.querySelector('.fa-thumbs-up').classList.remove('fa-solid');
            likeBtn.querySelector('.interaction-count').textContent = response.total_likes;
        }
    }
}