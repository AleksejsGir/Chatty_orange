document.addEventListener('DOMContentLoaded', function() {
    const assistant = document.querySelector('.assistant-container');
    const assistantImage = document.querySelector('.assistant-image');
    let menu = null;
    let hoverTimeout;
    let isMenuOpen = false;

    // AI Chat Elements
    const aiChatBody = document.getElementById('aiChatBody');
    const aiChatMessageInput = document.getElementById('aiChatMessageInput');
    const aiSendMessageBtn = document.getElementById('aiSendMessageBtn');
    const assistantModalElement = document.getElementById('aiAssistantModal');
    let assistantBootstrapModal = null;
    if (assistantModalElement) {
        assistantBootstrapModal = new bootstrap.Modal(assistantModalElement);
    }
    const assistantContainer = document.querySelector('.assistant-container'); // Для user_info

    // Новые кнопки для выбора типа действия
    const aiFaqBtn = document.getElementById('aiFaqBtn');
    const aiFeatureBtn = document.getElementById('aiFeatureBtn');
    let currentActionType = 'general_chat'; // Глобальная переменная для текущего типа действия

    // Создаем меню один раз при загрузке
    function createMenu() {
        if (!menu) {
            menu = document.createElement('div');
            menu.className = 'assistant-menu';
            menu.innerHTML = `
                <a href="#" onclick="return window.showRules()">Правила сайта</a>
                <a href="#" onclick="return window.showGuide()">Инструкция сайта</a>
                <a href="#" onclick="return window.showAIAssistant()">ИИ помощник</a>
            `;
            // assistant.appendChild(menu); // Больше не добавляем сюда, т.к. assistantContainer может быть null
            if (assistant) { // Добавляем меню, только если основной контейнер помощника существует
                assistant.appendChild(menu);
            } else {
                console.error("Элемент .assistant-container не найден. Меню не будет создано.");
                return; // Выход, если нет основного контейнера
            }
        }
    }

    // Показать меню с задержкой
    function showMenu() {
        if (!assistant) return; // Не показывать меню, если нет контейнера
        clearTimeout(hoverTimeout);
        if (!isMenuOpen) {
            createMenu(); // Убедимся, что меню создано
            if (!menu) return; // Если меню не удалось создать (например, нет assistantContainer)
            hoverTimeout = setTimeout(() => {
                menu.classList.add('show');
                isMenuOpen = true;
            }, 300);
        }
    }

    // Скрыть меню с задержкой
    window.hideMenu = function() {
        clearTimeout(hoverTimeout);
        if (menu && isMenuOpen) {
            hoverTimeout = setTimeout(() => {
                menu.classList.remove('show');
                isMenuOpen = false;
            }, 300);
        }
    }

    // Обработчики событий для меню
    if (assistantImage) {
        assistantImage.addEventListener('click', function(e) {
            e.stopPropagation();
            isMenuOpen ? window.hideMenu() : showMenu();
        });
        assistantImage.addEventListener('mouseenter', showMenu);
        assistantImage.addEventListener('mouseleave', () => {
            if (!isMenuOpen) return;
            window.hideMenu();
        });
    } else {
        console.warn("Элемент .assistant-image не найден. Функциональность меню может быть ограничена.");
    }

    // Обработчики для самого меню (если оно создано)
    // Эти обработчики нужно добавлять ПОСЛЕ создания меню, поэтому они могут быть в createMenu
    // или здесь с проверкой на существование menu.
    // Для простоты, если createMenu всегда вызывается перед showMenu, то menu должно существовать.
    // Обновление: Добавляем обработчики к menu только если menu существует.
    // Это лучше делать в createMenu или после явного вызова createMenu.
    // Однако, для текущей логики, где createMenu вызывается в showMenu,
    // menu может быть null при первом вызове addEventListener.
    // Безопаснее будет добавить эти слушатели после того, как menu точно создано.
    // Например, внутри createMenu, после menu.innerHTML.
    // Или, если мы хотим сохранить текущую структуру, нужно быть осторожнее.
    // Пока оставим так, но это потенциальное место для ошибки, если menu не успеет создаться.
    // Решение: Перенесем добавление слушателей внутрь createMenu или будем проверять menu.
    if (menu) {
        menu.addEventListener('mouseenter', () => clearTimeout(hoverTimeout));
        menu.addEventListener('mouseleave', window.hideMenu);
    }


    // Закрытие меню при клике вне его
    document.addEventListener('click', function(e) {
        if (isMenuOpen && assistant && !assistant.contains(e.target)) {
            window.hideMenu();
        }
    });

    // --- AI Assistant Chat Functions ---

    window.showAIAssistant = function() {
        if (aiChatBody) {
            // Очищаем чат и добавляем приветственное сообщение при каждом открытии
            aiChatBody.innerHTML = '';
            appendMessageToChat('Привет! Я твой Апельсиновый Помощник. Чем могу помочь?', 'ai');
        }
        if (assistantBootstrapModal) {
            assistantBootstrapModal.show();
        }
        if (window.hideMenu) window.hideMenu();
        return false;
    }

    function appendMessageToChat(message, sender) {
        if (!aiChatBody) return;
        const messageDiv = document.createElement('div');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'ai-message');
        if (sender === 'ai-thinking') { // специальный класс для "думает"
            messageDiv.classList.remove('ai-message'); // Удаляем, если был добавлен ai-message
            messageDiv.classList.add('thinking'); // Используем общий класс 'thinking'
        }

        const tempDiv = document.createElement('div');
        tempDiv.textContent = message; // Используем textContent для безопасности
        messageDiv.innerHTML = tempDiv.innerHTML.replace(/\n/g, '<br>'); // Заменяем \n на <br>

        aiChatBody.appendChild(messageDiv);
        aiChatBody.scrollTop = aiChatBody.scrollHeight;
    }

    async function sendChatMessage() {
        if (!aiChatMessageInput) return;
        const messageText = aiChatMessageInput.value.trim();
        if (messageText === '') return;

        appendMessageToChat(messageText, 'user');
        // Очищаем инпут ПОСЛЕ отправки сообщения и использования currentActionType
        // aiChatMessageInput.value = '';
        aiChatMessageInput.disabled = true;
        if(aiSendMessageBtn) aiSendMessageBtn.disabled = true;

        const requestData = {
            action_type: currentActionType, // Используем currentActionType
            user_input: messageText,
            user_info: {
                username: assistantContainer && assistantContainer.dataset.username ? assistantContainer.dataset.username : 'anonymous'
            }
        };

        // Используем appendMessageToChat для сообщения "думает"
        appendMessageToChat('Апельсинка думает...', 'ai-thinking');
        // Получаем ссылку на сообщение "думает", чтобы удалить его позже
        const thinkingMessageElement = aiChatBody.querySelector('.thinking:last-child');


        try {
            const response = await fetch('/assistant/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // 'X-CSRFToken': csrftoken // Раскомментировать, если CSRF используется
                },
                body: JSON.stringify(requestData)
            });

            if (thinkingMessageElement && thinkingMessageElement.parentNode === aiChatBody) {
                aiChatBody.removeChild(thinkingMessageElement);
            }

            if (!response.ok) {
                // Пытаемся получить JSON с ошибкой, или используем response.statusText
                let errorDetail = response.statusText;
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.error || errorData.detail || errorDetail;
                } catch (e) {
                    // Оставляем errorDetail как response.statusText, если JSON не парсится
                }
                console.error('Ошибка от сервера ИИ:', errorDetail);
                appendMessageToChat(`Ошибка: ${errorDetail}`, 'ai');
                return;
            }

            const responseData = await response.json();
            appendMessageToChat(responseData.response, 'ai');

        } catch (error) {
            if (thinkingMessageElement && thinkingMessageElement.parentNode === aiChatBody) {
                 aiChatBody.removeChild(thinkingMessageElement);
            }
            console.error('Сетевая ошибка или ошибка обработки ИИ ответа:', error);
            appendMessageToChat('Произошла сетевая ошибка или ошибка обработки ответа от ИИ. Попробуйте еще раз.', 'ai');
        } finally {
            if (aiChatMessageInput) {
                aiChatMessageInput.disabled = false;
                aiChatMessageInput.value = ''; // Очищаем здесь, после всех операций
                aiChatMessageInput.focus();
            }
            if(aiSendMessageBtn) aiSendMessageBtn.disabled = false;

            // Сброс currentActionType и активных классов кнопок
            currentActionType = 'general_chat';
            if (aiFaqBtn) aiFaqBtn.classList.remove('active');
            if (aiFeatureBtn) aiFeatureBtn.classList.remove('active');
        }
    }

    if (aiSendMessageBtn) {
        aiSendMessageBtn.addEventListener('click', sendChatMessage);
    }

    if (aiChatMessageInput) {
        aiChatMessageInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendChatMessage();
            }
        });

        aiChatMessageInput.addEventListener('input', function() {
            const messageText = aiChatMessageInput.value;
            // Сбрасываем тип, если текст не соответствует префиксам (или пустой)
            // Это позволяет пользователю стереть префикс и вернуться в general_chat
            if (!messageText.startsWith("Вопрос: ") && !messageText.startsWith("Функция: ")) {
                if (currentActionType !== 'general_chat') { // Только если был другой тип
                    currentActionType = 'general_chat';
                    if (aiFaqBtn) aiFaqBtn.classList.remove('active');
                    if (aiFeatureBtn) aiFeatureBtn.classList.remove('active');
                     // Можно добавить console.log для отладки смены типа
                    // console.log("Switched to general_chat due to input change");
                }
            } else if (messageText.startsWith("Вопрос: ") && currentActionType !== 'faq') {
                 currentActionType = 'faq';
                 if (aiFaqBtn) aiFaqBtn.classList.add('active');
                 if (aiFeatureBtn) aiFeatureBtn.classList.remove('active');
            } else if (messageText.startsWith("Функция: ") && currentActionType !== 'feature_explanation') {
                 currentActionType = 'feature_explanation';
                 if (aiFeatureBtn) aiFeatureBtn.classList.add('active');
                 if (aiFaqBtn) aiFaqBtn.classList.remove('active');
            }
        });
    }

    // Обработчики для новых кнопок
    if (aiFaqBtn) {
        aiFaqBtn.addEventListener('click', function() {
            currentActionType = 'faq';
            aiChatMessageInput.value = "Вопрос: ";
            aiChatMessageInput.focus();
            aiFaqBtn.classList.add('active');
            if (aiFeatureBtn) aiFeatureBtn.classList.remove('active');
        });
    }

    if (aiFeatureBtn) {
        aiFeatureBtn.addEventListener('click', function() {
            currentActionType = 'feature_explanation';
            aiChatMessageInput.value = "Функция: ";
            aiChatMessageInput.focus();
            aiFeatureBtn.classList.add('active');
            if (aiFaqBtn) aiFaqBtn.classList.remove('active');
        });
    }

    // --- End AI Assistant Chat Functions ---

    // Модальные окна для правил и инструкций
    window.showRules = function() {
        const rulesModalElement = document.getElementById('rulesModal');
        if (rulesModalElement) {
            const rulesModal = new bootstrap.Modal(rulesModalElement);
            if (rulesModal) rulesModal.show();
        }
        if (window.hideMenu) window.hideMenu();
        return false;
    }

    window.showGuide = function() {
        const guideModalElement = document.getElementById('guideModal');
        if (guideModalElement) {
            const guideModal = new bootstrap.Modal(guideModalElement);
            if (guideModal) guideModal.show();
        }
        if (window.hideMenu) window.hideMenu();
        return false;
    }
});