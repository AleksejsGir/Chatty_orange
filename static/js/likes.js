// static/js/likes.js
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            if (this.disabled) return;

            const postId = this.dataset.postId;
            const likeUrl = `/posts/${postId}/like/`;
            const likeIcon = this.querySelector('i');
            const likeCount = this.querySelector('.interaction-count');

            fetch(likeUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'ok') {
                    this.classList.toggle('active', data.liked);
                    likeIcon.classList.toggle('fa-regular', !data.liked);
                    likeIcon.classList.toggle('fa-solid', data.liked);
                    likeCount.textContent = data.total_likes;
                } else {
                    alert(data.message || 'Error processing like');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error: ' + error.message);
            });
        });
    });

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
document.querySelectorAll('.dislike-button').forEach(button => {
    button.addEventListener('click', async function(e) {
        e.preventDefault();
        const postId = this.dataset.postId;
        const dislikeUrl = `/posts/${postId}/dislike/`;
        const icon = this.querySelector('i');
        const count = this.querySelector('.interaction-count');

        try {
            const response = await fetch(dislikeUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });

            if (response.status === 403) {
                showLoginAlert();
                return;
            }

            const data = await response.json();

            if (data.status === 'ok') {
                // Обновляем дизлайк
                this.classList.toggle('active', data.disliked);
                icon.classList.toggle('fa-regular', !data.disliked);
                icon.classList.toggle('fa-solid', data.disliked);
                count.textContent = data.total_dislikes;

                // Обновляем лайк
                const likeButton = document.querySelector(`.like-button[data-post-id="${postId}"]`);
                if (likeButton) {
                    likeButton.querySelector('.interaction-count').textContent = data.total_likes;
                }
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Ошибка соединения с сервером');
        }
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