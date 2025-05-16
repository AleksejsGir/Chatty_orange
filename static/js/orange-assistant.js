// Функция для приветствия пользователя
function greetUser(username) {
    const assistant = document.getElementById('orange-assistant');
    assistant.innerHTML = `Привет, ${username}!`;
}

// Функция для прощания с пользователем
function goodbyeUser() {
    const assistant = document.getElementById('orange-assistant');
    assistant.innerHTML = 'Пока, пока!';
}

// Пример обработки регистрации пользователя
document.getElementById('register-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;

    // Отправка данных на сервер
    fetch('/register', {
        method: 'POST',
        body: JSON.stringify({ username: username }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            greetUser(username);
        }
    });
});

// Пример обработки входа пользователя
document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;

    // Отправка данных на сервер
    fetch('/login', {
        method: 'POST',
        body: JSON.stringify({ username: username }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            greetUser(username);
        }
    });
});

// Пример обработки выхода пользователя
document.getElementById('logout-button').addEventListener('click', function() {
    // Отправка запроса на выход
    fetch('/logout', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            goodbyeUser();
        }
    });
});
