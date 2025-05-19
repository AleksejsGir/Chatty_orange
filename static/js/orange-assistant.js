document.addEventListener('DOMContentLoaded', function() {
    const assistant = document.querySelector('.assistant-container');
    const assistantImage = document.querySelector('.assistant-image');
    let menu = null;
    let hoverTimeout;
    let isMenuOpen = false;

    // Создаем меню один раз при загрузке
    function createMenu() {
        if (!menu) {
            menu = document.createElement('div');
            menu.className = 'assistant-menu';
            menu.innerHTML = `
                <a href="#" onclick="showRules()">Правила сайта</a>
                <a href="#" onclick="showGuide()">Инструкция сайта</a>
                <a href="#" onclick="showAIAssistant()">ИИ помощник</a>
<!--                <button class="close-menu-btn" onclick="hideMenu()">Закрыть</button>-->
                <button class="close-menu-btn" onclick="window.hideMenu()">Закрыть</button>
            `;
            assistant.appendChild(menu);
        }
    }

    window.showAIAssistant = function() {
        new bootstrap.Modal('#aiAssistantModal').show();
        hideMenu();
        return false;
    }

    // // Создаем меню один раз при загрузке
    // function createMenu() {
    //     if (!menu) {
    //         menu = document.createElement('div');
    //         menu.className = 'assistant-menu';
    //         menu.innerHTML = `
    //     <a href="#" onclick="showRules()">Правила сайта</a>
    //     <a href="#" onclick="showGuide()">Инструкция сайта</a>
    //     <a href="#" onclick="showAIAssistant()">ИИ помощник</a>
    //     <button class="close-menu-btn" onclick="hideMenu()">Закрыть</button>
    //   `;
    //         assistant.appendChild(menu);
    //     }
    // }

    // Показать меню с задержкой
    function showMenu() {
        clearTimeout(hoverTimeout);
        if (!isMenuOpen) {
            createMenu();
            hoverTimeout = setTimeout(() => {
                menu.classList.add('show');
                isMenuOpen = true;
            }, 300); // Небольшая задержка для предотвращения случайного открытия
        }
    }

    // Скрыть меню с задержкой
    function hideMenu() {
        clearTimeout(hoverTimeout);
        if (menu && isMenuOpen) {
            hoverTimeout = setTimeout(() => {
                menu.classList.remove('show');
                isMenuOpen = false;
            }, 300); // Даем время увести курсор на меню
        }
    }
    window.hideMenu = hideMenu;

    // Обработчики событий
    assistantImage.addEventListener('click', function(e) {
        e.stopPropagation();
        if (isMenuOpen) {
            hideMenu();
        } else {
            showMenu();
        }
    });

    // Закрытие меню при клике вне его
    document.addEventListener('click', function(e) {
        if (isMenuOpen && !assistant.contains(e.target)) {
            hideMenu();
        }
    });

    // Обработчики событий для наведения
    assistantImage.addEventListener('mouseenter', showMenu);
    assistantImage.addEventListener('mouseleave', () => {
        if (!isMenuOpen) return;
        hideMenu();
    });
    // menu?.addEventListener('mouseenter', () => clearTimeout(hoverTimeout));
    // menu?.addEventListener('mouseleave', hideMenu);
    menu?.addEventListener('mouseenter', () => {
        clearTimeout(hoverTimeout);
    });

    menu?.addEventListener('mouseleave', () => {
        if (isMenuOpen) hideMenu();
    });

    // Модальные окна
    window.showRules = function() {
        new bootstrap.Modal('#rulesModal').show();
        return false;
    }

    window.showGuide = function() {
        new bootstrap.Modal('#guideModal').show();
        return false;
    }

    window.showAIAssistant = function() {
        new bootstrap.Modal('#aiAssistantModal').show();
        return false;
    }
});