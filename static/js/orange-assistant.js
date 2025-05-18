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

document.addEventListener('DOMContentLoaded', function() {
    // Удалите дублирующийся DOMContentLoaded в конце файла

    const assistant = document.getElementById('orangeAssistant');
    const dialogBox = document.getElementById('dialogBox');

    if (!assistant || !dialogBox) {
        console.error('Не найдены элементы ассистента!');
        return;
    }

    // Показываем/скрываем диалоговое окно при наведении
    assistant.addEventListener('mouseenter', function() {
        dialogBox.style.display = 'block';
        setTimeout(() => {
            dialogBox.style.opacity = '1';
        }, 10);
    });

    assistant.addEventListener('mouseleave', function() {
        dialogBox.style.opacity = '0';
        setTimeout(() => {
            dialogBox.style.display = 'none';
        }, 300);
    });

    // Персонализированное приветствие, если пользователь авторизован
    const container = document.querySelector('.assistant-container');
    if (container) {
        const username = container.dataset.username;
        if (username) {
            const greeting = dialogBox.querySelector('.greeting');
            if (greeting) {
                greeting.textContent = `Привет, ${username}!`;
            }
        }
    }
});

// Удалите остальной код, если он не используется
// Или оставьте только то, что действительно нужно