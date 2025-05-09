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