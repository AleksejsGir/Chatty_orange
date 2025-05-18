// Обновленный orange-assistant.js
document.addEventListener('DOMContentLoaded', function() {
  const assistant = document.querySelector('.assistant-container');
  const dialogBox = document.querySelector('.dialog-box');
  const assistantImage = document.querySelector('.assistant-image');
  let menuTimeout;

  // Показать/скрыть меню
  assistant.addEventListener('mouseenter', () => {
    clearTimeout(menuTimeout);
    showMenu();
  });

  assistant.addEventListener('mouseleave', () => {
    menuTimeout = setTimeout(hideMenu, 300);
  });

  function showMenu() {
    const menu = document.createElement('div');
    menu.className = 'assistant-menu';
    menu.innerHTML = `
      <a href="#" onclick="showRules()">Правила сайта.</a>
      <a href="#" onclick="showGuide()">Инструкция сайта.</a>
      <a href="#">ИИ помощник.</a>
      <button class="close-menu-btn" onclick="hideMenu()">Закрыть</button>
    `;
    assistant.appendChild(menu);
    menu.classList.add('show');
  }

  function hideMenu() {
    const menu = document.querySelector('.assistant-menu');
    if(menu) menu.remove();
  }
  window.hideMenu = hideMenu;

  

  // Временные сообщения
  window.showWelcomeMessage = function(username) {
    const msg = document.createElement('div');
    msg.className = 'temporary-message';
    msg.textContent = `Привет, ${username}!`;
    document.body.appendChild(msg);

    setTimeout(() => {
      msg.remove();
    }, 15000);
  }

  window.showGoodbyeMessage = function() {
    const msg = document.createElement('div');
    msg.className = 'temporary-message';
    msg.textContent = 'Пока! Пока! До встречи!';
    document.body.appendChild(msg);

    setTimeout(() => {
      msg.remove();
    }, 15000);
  }

  // Модальные окна
  window.showRules = function() {
    new bootstrap.Modal('#rulesModal').show();
    hideMenu();
  }

  window.showGuide = function() {
    new bootstrap.Modal('#guideModal').show();
    hideMenu();
  }
});

// Интеграция с системой аутентификации
document.addEventListener('userLoggedIn', function(e) {
  showWelcomeMessage(e.detail.username);
});

document.addEventListener('userLoggedOut', function() {
  showGoodbyeMessage();
});