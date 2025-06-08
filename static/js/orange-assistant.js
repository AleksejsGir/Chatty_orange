document.addEventListener('DOMContentLoaded', function() {
    const CHAT_OPEN_STATE_KEY = 'chattyOrangeChatOpen';

    const assistant = document.querySelector('.assistant-container');
    const assistantImage = document.querySelector('.assistant-image');
    let menu = null;
    let isMenuOpen = false;
    let isMouseOverAssistant = false;
    let isMouseOverMenu = false;

    // Chat Widget Elements (НЕ модальное окно!)
    let chatWidget = null;
    let aiChatBody = null;
    let aiChatMessageInput = null;
    let aiSendMessageBtn = null;
    let isChatOpen = false;
    let isChatMinimized = false;

    const assistantContainer = document.querySelector('.assistant-container');
    const currentUsername = assistantContainer ? assistantContainer.dataset.username : null;

    let currentActionType = 'general_chat';

    // НОВЫЕ КОНСТАНТЫ ДЛЯ ИСТОРИИ ЧАТА
    const CHAT_HISTORY_KEY = 'chattyOrangeChatHistory';
    const MAX_MESSAGES = 100; // Максимум сообщений в истории

    // Interactive Tour Elements
    let currentTourStep = 1;
    const MAX_TOUR_STEPS = 4;
    let interactiveTourModal = null;
    let tourModalBody = null;
    let tourStepNumberSpan = null;
    let nextTourStepBtn = null;
    let endTourBtn = null;
    let closeTourModalBtn = null;
    let nextButtonListenerAttached = false;

    function getTourStorageKey() {
        if (currentUsername && currentUsername !== 'Гость' && currentUsername.trim() !== '') {
            return `chattyOrangeTourCompleted_${currentUsername}`;
        }
        return 'chattyOrangeTourCompleted_guest';
    }

    // =========================
    // ФУНКЦИИ ДЛЯ РАБОТЫ С ИСТОРИЕЙ ЧАТА
    // =========================

    /**
     * Генерирует уникальный ID для сообщения
     */
    function generateMessageId() {
        return Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Получает ключ для истории чата конкретного пользователя
     */
    function getChatHistoryKey() {
        const username = assistantContainer?.dataset.username || 'guest';
        return `${CHAT_HISTORY_KEY}_${username}`;
    }

    /**
     * Загружает историю чата из localStorage
     */
    function loadChatHistory() {
        try {
            const historyKey = getChatHistoryKey();
            const savedHistory = localStorage.getItem(historyKey);

            if (savedHistory) {
                const history = JSON.parse(savedHistory);

                // Проверяем структуру данных
                if (history && Array.isArray(history.messages)) {
                    console.log(`Загружена история чата: ${history.messages.length} сообщений`);
                    return history;
                }
            }

            // Возвращаем пустую историю, если ничего не найдено
            return {
                messages: [],
                lastUpdate: Date.now()
            };

        } catch (error) {
            console.error('Ошибка при загрузке истории чата:', error);
            return {
                messages: [],
                lastUpdate: Date.now()
            };
        }
    }

    /**
     * Сохраняет историю чата в localStorage
     */
    function saveChatHistory(history) {
        try {
            const historyKey = getChatHistoryKey();

            // Обновляем время последнего изменения
            history.lastUpdate = Date.now();

            // Ограничиваем количество сообщений
            if (history.messages.length > MAX_MESSAGES) {
                history.messages = history.messages.slice(-MAX_MESSAGES);
                console.log(`История чата обрезана до ${MAX_MESSAGES} сообщений`);
            }

            localStorage.setItem(historyKey, JSON.stringify(history));
            console.log(`История чата сохранена: ${history.messages.length} сообщений`);

        } catch (error) {
            console.error('Ошибка при сохранении истории чата:', error);

            // Если места не хватает, пробуем очистить старые сообщения
            if (error.name === 'QuotaExceededError') {
                console.log('Превышен лимит localStorage, очищаем старые сообщения...');
                history.messages = history.messages.slice(-50); // Оставляем только 50 последних
                try {
                    localStorage.setItem(historyKey, JSON.stringify(history));
                    console.log('История чата сохранена после очистки');
                } catch (secondError) {
                    console.error('Не удалось сохранить даже после очистки:', secondError);
                }
            }
        }
    }

    /**
     * Добавляет новое сообщение в историю
     */
    function addMessageToHistory(messageText, sender, messageId = null) {
        const history = loadChatHistory();

        const newMessage = {
            id: messageId || generateMessageId(),
            text: messageText,
            sender: sender,
            timestamp: Date.now()
        };

        history.messages.push(newMessage);
        saveChatHistory(history);

        return newMessage;
    }

    /**
     * Восстанавливает историю чата в интерфейсе
     */
    function restoreChatHistory() {
        if (!aiChatBody) {
            console.log('aiChatBody не найден, пропускаем восстановление истории');
            return;
        }

        const history = loadChatHistory();

        if (history.messages.length === 0) {
            console.log('История чата пуста, показываем приветствие');
            // Показываем обычное приветствие для нового чата
            appendMessageToChat('Привет! 👋 Я твой Апельсиновый Помощник! Чем могу помочь сегодня?', 'ai', false, false);
            appendQuickActions();
            return;
        }

        console.log(`Восстанавливаем ${history.messages.length} сообщений из истории`);

        // Очищаем текущий чат
        aiChatBody.innerHTML = '';

        // Добавляем индикатор восстановления
        const restoreIndicator = document.createElement('div');
        restoreIndicator.className = 'restore-indicator';
        restoreIndicator.innerHTML = `
            <div style="text-align: center; padding: 10px; color: #f97316; font-size: 12px; border-bottom: 1px solid #eee; margin-bottom: 10px;">
                <i class="fas fa-history"></i> История чата восстановлена (${history.messages.length} сообщений)
            </div>
        `;
        aiChatBody.appendChild(restoreIndicator);

        // Восстанавливаем все сообщения
        history.messages.forEach(message => {
            appendMessageToChat(message.text, message.sender, false, false); // Не сохраняем в историю повторно
        });

        // Добавляем быстрые действия в конце, если последнее сообщение от ИИ
        const lastMessage = history.messages[history.messages.length - 1];
        if (lastMessage && lastMessage.sender === 'ai') {
            appendQuickActions();
        }

        // Прокручиваем в самый низ
        setTimeout(() => {
            aiChatBody.scrollTop = aiChatBody.scrollHeight;
        }, 100);
    }

    /**
     * Очищает историю чата
     */
    function clearChatHistory() {
        try {
            const historyKey = getChatHistoryKey();
            localStorage.removeItem(historyKey);

            if (aiChatBody) {
                aiChatBody.innerHTML = '';
                appendMessageToChat('История чата очищена! 🗑️', 'ai', false, false);
                appendMessageToChat('Привет! 👋 Я твой Апельсиновый Помощник! Чем могу помочь?', 'ai', false, false);
                appendQuickActions();
            }

            console.log('История чата очищена');

        } catch (error) {
            console.error('Ошибка при очистке истории чата:', error);
        }
    }

    /**
     * Получает статистику по истории чата
     */
    function getChatHistoryStats() {
        const history = loadChatHistory();

        const userMessages = history.messages.filter(m => m.sender === 'user').length;
        const aiMessages = history.messages.filter(m => m.sender === 'ai').length;

        return {
            totalMessages: history.messages.length,
            userMessages: userMessages,
            aiMessages: aiMessages,
            lastUpdate: history.lastUpdate ? new Date(history.lastUpdate) : null
        };
    }

    // Автоматическое определение типа команды
    function detectCommandType(messageText) {
        const lowerText = messageText.toLowerCase().trim();

        const userSearchPatterns = [
            /найди пользователя/i, /найти пользователя/i, /ищи пользователя/i, /искать пользователя/i,
            /найди юзера/i, /пользователь \w+/i, /профиль \w+/i, /кто такой \w+/i, /в профиле \w+/i, /@\w+/i
        ];

        if (userSearchPatterns.some(pattern => pattern.test(lowerText))) {
            return 'find_user_by_username';
        }

        const postSearchPatterns = [
            /найди пост/i, /найти пост/i, /ищи пост/i, /найди стать/i, /найти стать/i,
            /посты про/i, /статьи про/i, /посты о/i, /статьи о/i
        ];

        if (postSearchPatterns.some(pattern => pattern.test(lowerText))) {
            return 'find_post_by_keyword';
        }

        const userPostsPatterns = [
            /статьи у \w+/i, /посты у \w+/i, /какие статьи у/i, /какие посты у/i,
            /что писал \w+/i, /посты пользователя/i, /статьи пользователя/i
        ];

        if (userPostsPatterns.some(pattern => pattern.test(lowerText))) {
            return 'find_post_by_keyword';
        }

        const postDetailPatterns = [
            /расскажи о посте/i, /пост номер/i, /пост \d+/i, /пост id/i, /детали поста/i, /покажи пост/i
        ];

        if (postDetailPatterns.some(pattern => pattern.test(lowerText))) {
            return 'get_post_details';
        }

        const activityPatterns = [
            /что нового у/i, /активность пользователя/i, /что делает \w+/i, /последние посты/i, /недавняя активность/i
        ];

        if (activityPatterns.some(pattern => pattern.test(lowerText))) {
            return 'get_user_activity';
        }

        const recommendationPatterns = [
            /кого почитать/i, /рекомендации/i, /посоветуй авторов/i, /интересные авторы/i, /на кого подписаться/i
        ];

        if (recommendationPatterns.some(pattern => pattern.test(lowerText))) {
            return 'subscription_recommendations';
        }

        const contentCheckPatterns = [
            /проверь текст/i, /проверить пост/i, /можно ли публиковать/i, /соответствует правилам/i
        ];

        if (contentCheckPatterns.some(pattern => pattern.test(lowerText))) {
            return 'check_post_content';
        }

        const ideasPatterns = [
            /идеи для пост/i, /что написать/i, /тема для пост/i, /предложи тему/i, /идеи контента/i
        ];

        if (ideasPatterns.some(pattern => pattern.test(lowerText))) {
            return 'generate_post_ideas';
        }

        const profilePatterns = [
            /моя статистика/i, /анализ профиля/i, /мой прогресс/i, /как дела у меня/i
        ];

        if (profilePatterns.some(pattern => pattern.test(lowerText))) {
            return 'analyze_profile';
        }

        return 'general_chat';
    }

    // Создаем меню помощника
    function createMenu() {
        if (!menu) {
            menu = document.createElement('div');
            menu.className = 'assistant-menu';
            menu.innerHTML = `
                <h6 class="menu-title">🍊 Апельсиновый Помощник</h6>
                <div class="menu-section">
                    <a href="#" onclick="return window.showRules()">
                        <i class="fas fa-book-open me-2"></i>Правила сайта
                    </a>
                    <a href="#" onclick="return window.showGuide()">
                        <i class="fas fa-info-circle me-2"></i>Инструкция
                    </a>
                    <a href="#" id="startTourBtn">
                        <i class="fas fa-route me-2"></i>Пройти тур
                    </a>
                </div>
                <div class="menu-section">
                    <a href="#" id="showRecommendationsBtn">
                        <i class="fas fa-user-plus me-2"></i>Кого почитать?
                    </a>
                    <a href="#" id="showProfileStatsBtn">
                        <i class="fas fa-chart-line me-2"></i>Моя статистика
                    </a>
                    <a href="#" id="showPostIdeasBtn">
                        <i class="fas fa-lightbulb me-2"></i>Идеи для постов
                    </a>
                </div>
                <div class="menu-section">
                    <a href="#" onclick="return window.showAIAssistant()">
                        <i class="fas fa-comments me-2"></i>Открыть чат
                    </a>
                </div>
            `;
            if (assistant) {
                assistant.appendChild(menu);

                menu.addEventListener('mouseenter', function() {
                    isMouseOverMenu = true;
                });

                menu.addEventListener('mouseleave', function() {
                    isMouseOverMenu = false;
                    checkAndHideMenu();
                });
            }
        }
    }

    // Показать/скрыть меню
    function showMenu() {
        if (!assistant) return;
        createMenu();
        if (!menu) return;

        isMenuOpen = true;
        menu.classList.add('show');

        if (typeof gsap !== 'undefined') {
            gsap.to(assistantImage, { scale: 1.1, rotation: -10, duration: 0.3 });
        }
    }

    function hideMenu() {
        if (menu && isMenuOpen) {
            isMenuOpen = false;
            menu.classList.remove('show');

            if (typeof gsap !== 'undefined') {
                gsap.to(assistantImage, { scale: 1, rotation: 0, duration: 0.3 });
            }
        }
    }

    function checkAndHideMenu() {
        setTimeout(() => {
            if (!isMouseOverAssistant && !isMouseOverMenu && isMenuOpen) {
                hideMenu();
            }
        }, 100);
    }

    window.hideMenu = hideMenu;

    // Обработчики событий для помощника
    if (assistantImage) {
        assistantImage.addEventListener('click', function(e) {
            e.stopPropagation();
            if (isMenuOpen) {
                hideMenu();
            } else {
                showMenu();
            }
        });

        assistantImage.addEventListener('mouseenter', function() {
            isMouseOverAssistant = true;
            if (!isMenuOpen) showMenu();
        });

        assistantImage.addEventListener('mouseleave', function() {
            isMouseOverAssistant = false;
            checkAndHideMenu();
        });
    }

    // Закрытие меню при клике вне его
    document.addEventListener('click', function(e) {
        if (isMenuOpen && assistant && !assistant.contains(e.target) &&
            !e.target.closest('.chat-widget')) {
            hideMenu();
        }
    });

    // ============ НОВЫЙ ЧАТ ВИДЖЕТ (НЕ МОДАЛЬНОЕ ОКНО!) ============
    function createChatWidget() {
        if (chatWidget) return;

        chatWidget = document.createElement('div');
        chatWidget.className = 'chat-widget';
        chatWidget.innerHTML = `
            <div class="chat-widget-header">
                <div class="chat-widget-resizer"></div>
                <div class="chat-widget-title">
                    <img src="/static/images/orange.png" alt="Orange" style="width: 24px; height: 24px; margin-right: 8px;">
                    <span>Апельсиновый Помощник</span>
                </div>
                <div class="chat-widget-controls">
                    <button class="chat-btn chat-btn-minimize" onclick="window.minimizeChat()" title="Свернуть">
                        <i class="fas fa-minus"></i>
                    </button>
                    <button class="chat-btn chat-btn-expand" onclick="window.expandChat()" title="Развернуть" style="display: none;">
                        <i class="fas fa-expand"></i>
                    </button>
                    <button class="chat-btn chat-btn-close" onclick="window.closeChat()" title="Закрыть">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="chat-widget-body">
                <!-- Чат контент будет добавлен сюда -->
            </div>
            <div class="chat-widget-footer">
                <textarea class="chat-input" placeholder="Спроси меня что-нибудь..." rows="2"></textarea>
                <button class="chat-send-btn">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        `;

        document.body.appendChild(chatWidget);

        // Получаем элементы
        aiChatBody = chatWidget.querySelector('.chat-widget-body');
        aiChatMessageInput = chatWidget.querySelector('.chat-input');
        aiSendMessageBtn = chatWidget.querySelector('.chat-send-btn');

        // Обработчики событий
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
        }

        // ИСПРАВЛЕННАЯ логика изменения размера виджета
        const resizer = chatWidget.querySelector('.chat-widget-resizer');
        if (resizer) {
            resizer.addEventListener('mousedown', function(e_mousedown) {
                e_mousedown.preventDefault();

                const initialWidth = chatWidget.offsetWidth;
                const initialHeight = chatWidget.offsetHeight;
                const initialMouseX = e_mousedown.clientX;
                const initialMouseY = e_mousedown.clientY;

                const computedStyle = getComputedStyle(chatWidget);
                const initialRight = parseInt(computedStyle.right, 10) || 20;
                const initialBottom = parseInt(computedStyle.bottom, 10) || 20;

                const minWidth = 300;
                const minHeight = 200;
                const maxWidth = window.innerWidth - initialRight - 50;
                const maxHeight = window.innerHeight - initialBottom - 50;

                chatWidget.classList.add('resizing');
                document.body.classList.add('resizing-chat');

                function handleMouseMove(e_mousemove) {
                    const deltaX = e_mousemove.clientX - initialMouseX;
                    const deltaY = e_mousemove.clientY - initialMouseY;

                    let newWidth = initialWidth - deltaX;
                    let newHeight = initialHeight - deltaY;

                    newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
                    newHeight = Math.max(minHeight, Math.min(maxHeight, newHeight));

                    // ВАЖНО: устанавливаем и width, и height
                    chatWidget.style.width = newWidth + 'px';
                    chatWidget.style.height = newHeight + 'px';
                    chatWidget.style.right = initialRight + 'px';
                    chatWidget.style.bottom = initialBottom + 'px';
                    chatWidget.style.left = 'auto';
                    chatWidget.style.top = 'auto';
                }

                function handleMouseUp() {
                    document.removeEventListener('mousemove', handleMouseMove);
                    document.removeEventListener('mouseup', handleMouseUp);

                    chatWidget.classList.remove('resizing');
                    document.body.classList.remove('resizing-chat');

                    // Сохраняем размеры
                    try {
                        localStorage.setItem('chattyOrangeChatWidth', chatWidget.offsetWidth);
                        localStorage.setItem('chattyOrangeChatHeight', chatWidget.offsetHeight);
                        console.log(`Сохранены размеры чата: ${chatWidget.offsetWidth}x${chatWidget.offsetHeight}`);
                    } catch (e) {
                        console.log('Не удалось сохранить размеры чата');
                    }
                }

                document.addEventListener('mousemove', handleMouseMove);
                document.addEventListener('mouseup', handleMouseUp);
            });
        }

        // Восстанавливаем сохраненные размеры чата
        restoreChatSize();
    }

    // Функция восстановления размеров чата
    function restoreChatSize() {
        try {
            const savedWidth = localStorage.getItem('chattyOrangeChatWidth');
            const savedHeight = localStorage.getItem('chattyOrangeChatHeight');

            if (savedWidth && savedHeight) {
                const width = parseInt(savedWidth, 10);
                const height = parseInt(savedHeight, 10);

                // Проверяем, что размеры корректные
                const minWidth = 300;
                const minHeight = 200;
                const maxWidth = window.innerWidth - 50;
                const maxHeight = window.innerHeight - 50;

                if (width >= minWidth && width <= maxWidth &&
                    height >= minHeight && height <= maxHeight) {

                    chatWidget.style.width = width + 'px';
                    chatWidget.style.height = height + 'px';

                    console.log(`Восстановлены размеры чата: ${width}x${height}`);
                }
            } else {
                // Устанавливаем размеры по умолчанию
                chatWidget.style.width = '380px';
                chatWidget.style.height = '600px';
            }
        } catch (e) {
            console.log('Не удалось восстановить размеры чата:', e);
            // Устанавливаем размеры по умолчанию при ошибке
            chatWidget.style.width = '380px';
            chatWidget.style.height = '600px';
        }
    }

    // ИЗМЕНЕННАЯ ФУНКЦИЯ showAIAssistant - теперь восстанавливает историю
    window.showAIAssistant = function() {
        createChatWidget();

        if (!isChatOpen) {
            if (aiChatBody && !isChatMinimized) {
                aiChatBody.innerHTML = '';

                // НОВОЕ: Восстанавливаем историю вместо показа приветствия
                restoreChatHistory();
            }

            chatWidget.style.display = 'flex';
            isChatOpen = true;
            localStorage.setItem(CHAT_OPEN_STATE_KEY, 'true');

            if (isChatMinimized) {
                expandChat();
            }
        }

        if (window.hideMenu) window.hideMenu();
        return false;
    }

    window.minimizeChat = function() {
        if (!chatWidget) return;

        isChatMinimized = true;
        localStorage.setItem(CHAT_OPEN_STATE_KEY, 'true'); // Keep chat "open" conceptually
        chatWidget.classList.add('minimized');

        const minimizeBtn = chatWidget.querySelector('.chat-btn-minimize');
        const expandBtn = chatWidget.querySelector('.chat-btn-expand');

        if (minimizeBtn) minimizeBtn.style.display = 'none';
        if (expandBtn) expandBtn.style.display = 'inline-block';
    }

    window.expandChat = function() {
        if (!chatWidget) return;

        isChatMinimized = false;
        chatWidget.classList.remove('minimized');

        const minimizeBtn = chatWidget.querySelector('.chat-btn-minimize');
        const expandBtn = chatWidget.querySelector('.chat-btn-expand');

        if (minimizeBtn) minimizeBtn.style.display = 'inline-block';
        if (expandBtn) expandBtn.style.display = 'none';
    }

    window.closeChat = function() {
        if (!chatWidget) return;

        chatWidget.style.display = 'none';
        isChatOpen = false;
        localStorage.setItem(CHAT_OPEN_STATE_KEY, 'false');
        isChatMinimized = false;
    }

    // РАСШИРЕННАЯ ФУНКЦИЯ appendQuickActions - добавлены новые кнопки
    function appendQuickActions() {
        const quickActionsDiv = document.createElement('div');
        quickActionsDiv.className = 'quick-actions mt-3';
        quickActionsDiv.innerHTML = `
            <div class="d-flex flex-wrap gap-2 mb-2">
                <button class="btn btn-sm btn-outline-warning quick-action" data-action="help">
                    <i class="fas fa-question-circle"></i> Что ты умеешь?
                </button>
                <button class="btn btn-sm btn-outline-info quick-action" data-action="tour">
                    <i class="fas fa-route"></i> Тур по сайту
                </button>
            </div>
            <div class="d-flex flex-wrap gap-2 mb-2">
                <button class="btn btn-sm btn-outline-success quick-action" data-action="ideas">
                    <i class="fas fa-lightbulb"></i> Идеи для постов
                </button>
                <button class="btn btn-sm btn-outline-primary quick-action" data-action="stats">
                    <i class="fas fa-chart-line"></i> Моя статистика
                </button>
            </div>
            <div class="d-flex flex-wrap gap-2">
                <button class="btn btn-sm btn-outline-secondary quick-action" data-action="history-stats">
                    <i class="fas fa-history"></i> Статистика чата
                </button>
                <button class="btn btn-sm btn-outline-danger quick-action" data-action="clear-history">
                    <i class="fas fa-trash"></i> Очистить историю
                </button>
            </div>
        `;
        aiChatBody.appendChild(quickActionsDiv);

        quickActionsDiv.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', function() {
                const action = this.dataset.action;
                handleQuickAction(action);
            });
        });
    }

    // РАСШИРЕННАЯ ФУНКЦИЯ handleQuickAction - добавлены новые действия
    function handleQuickAction(action) {
        switch(action) {
            case 'help':
                currentActionType = 'faq';
                aiChatMessageInput.value = "Что ты умеешь?";
                sendChatMessage();
                break;
            case 'tour':
                window.startInteractiveTour();
                break;
            case 'ideas':
                currentActionType = 'generate_post_ideas';
                appendMessageToChat("Генерирую идеи для постов...", 'user');
                sendChatMessage();
                break;
            case 'stats':
                currentActionType = 'analyze_profile';
                appendMessageToChat("Анализирую твою статистику...", 'user');
                sendChatMessage();
                break;
            // НОВЫЕ ДЕЙСТВИЯ:
            case 'history-stats':
                showChatHistoryStats();
                break;
            case 'clear-history':
                confirmClearHistory();
                break;
        }
    }

    // ИЗМЕНЕННАЯ ФУНКЦИЯ appendMessageToChat - добавлен параметр saveToHistory
    function appendMessageToChat(message, sender, scrollToMessage = false, saveToHistory = true) {
        if (!aiChatBody) return;

        const messageDiv = document.createElement('div');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'ai-message');

        if (sender === 'ai-thinking') {
            messageDiv.classList.remove('ai-message');
            messageDiv.classList.add('thinking');
        }

        if (sender === 'ai') {
            messageDiv.id = 'ai-message-' + Date.now();
        }

        // Форматирование с ПРАВИЛЬНЫМИ ссылками (НЕ закрывают чат)
        const formattedMessage = formatMessage(message);
        messageDiv.innerHTML = formattedMessage;

        aiChatBody.appendChild(messageDiv);

        // НОВОЕ: Сохраняем в историю (если не восстанавливаем из истории)
        if (saveToHistory && (sender === 'user' || sender === 'ai')) {
            addMessageToHistory(message, sender);
        }

        if (sender === 'user') {
            aiChatBody.scrollTop = aiChatBody.scrollHeight;
        } else if (sender === 'ai' && scrollToMessage) {
            setTimeout(() => {
                const messageTop = messageDiv.offsetTop - 20;
                aiChatBody.scrollTo({
                    top: messageTop,
                    behavior: 'smooth'
                });
            }, 100);
        }

        if (typeof gsap !== 'undefined') {
            gsap.from(messageDiv, { opacity: 0, y: 20, duration: 0.3 });
        }

        return messageDiv;
    }

    function formatMessage(message) {
        let formatted = message
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/__(.*?)__/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');

        // ИСПРАВЛЕНО: ссылки НЕ закрывают чат, открываются в том же окне
        formatted = formatted.replace(
            /(Ссылка|ссылка):\s*(\/[^\s<]+)/g,
            '<a href="$2" class="chat-link" data-url="$2">Перейти к посту</a>'
        );

        formatted = formatted.replace(/([\u{1F300}-\u{1F9FF}])/gu, '<span class="emoji">$1</span>');

        return formatted;
    }

    // Обработка кликов по ссылкам в чате (НЕ закрывают чат!)
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('chat-link')) {
            e.preventDefault();
            const url = e.target.getAttribute('data-url');
            if (url) {
                // Переходим по ссылке БЕЗ закрытия чата
                window.location.href = url;
            }
        }
    });

    // Отправка сообщений
    async function sendChatMessage() {
        if (!aiChatMessageInput) return;

        const messageText = aiChatMessageInput.value.trim();

        if (currentActionType === 'general_chat' && messageText) {
            const detectedType = detectCommandType(messageText);
            currentActionType = detectedType;
            console.log(`Auto-detected command type: ${detectedType} for message: "${messageText}"`);
        }

        if (messageText && currentActionType === 'general_chat') {
            appendMessageToChat(messageText, 'user');
        } else if (messageText && currentActionType !== 'general_chat') {
            appendMessageToChat(messageText, 'user');
        }

        if (aiChatMessageInput) {
            aiChatMessageInput.disabled = true;
        }
        if (aiSendMessageBtn) {
            aiSendMessageBtn.disabled = true;
        }

        const requestData = {
            action_type: currentActionType,
            user_input: messageText,
            user_info: {
                username: assistantContainer?.dataset.username || 'Гость'
            }
        };

        const thinkingMessage = createThinkingMessage();
        aiChatBody.appendChild(thinkingMessage);

        try {
            const response = await fetch('/assistant/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            thinkingMessage.remove();

            if (!response.ok) {
                let errorDetail = response.statusText;
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.error || errorData.detail || errorDetail;
                } catch (e) {}
                appendMessageToChat(`❌ Ошибка: ${errorDetail}`, 'ai');
                return;
            }

            const responseData = await response.json();
            appendMessageToChat(responseData.response, 'ai', true);

        } catch (error) {
            thinkingMessage.remove();
            console.error('Ошибка:', error);
            appendMessageToChat('😔 Произошла ошибка. Попробуй еще раз!', 'ai');
        } finally {
            if (aiChatMessageInput) {
                aiChatMessageInput.disabled = false;
                aiChatMessageInput.value = '';
                aiChatMessageInput.focus();
            }
            if (aiSendMessageBtn) {
                aiSendMessageBtn.disabled = false;
            }
            currentActionType = 'general_chat';
            resetActionButtons();
        }
    }

    function createThinkingMessage() {
        const thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'thinking-message';
        thinkingDiv.innerHTML = `
            <div class="thinking-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span class="thinking-text">Апельсинка думает...</span>
        `;
        return thinkingDiv;
    }

    function resetActionButtons() {
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.classList.remove('active');
        });
    }

    // НОВЫЕ ФУНКЦИИ ДЛЯ УПРАВЛЕНИЯ ИСТОРИЕЙ
    function showChatHistoryStats() {
        const stats = getChatHistoryStats();

        const statsMessage = `📊 **Статистика вашего чата:**

💬 Всего сообщений: ${stats.totalMessages}
👤 Ваших сообщений: ${stats.userMessages}  
🍊 Ответов помощника: ${stats.aiMessages}

${stats.lastUpdate ? `📅 Последнее обновление: ${stats.lastUpdate.toLocaleDateString()} в ${stats.lastUpdate.toLocaleTimeString()}` : ''}

💡 История автоматически сохраняется и восстанавливается при переходах между страницами!`;

        appendMessageToChat(statsMessage, 'ai', true);
    }

    function confirmClearHistory() {
        const confirmMessage = `🗑️ **Очистка истории чата**

Вы уверены, что хотите удалить всю историю переписки? Это действие нельзя отменить.

Нажмите "Очистить историю" еще раз, чтобы подтвердить, или напишите что-нибудь другое, чтобы отменить.`;

        appendMessageToChat(confirmMessage, 'ai', true);

        // Добавляем специальную кнопку подтверждения
        const confirmDiv = document.createElement('div');
        confirmDiv.className = 'confirm-clear-history mt-2';
        confirmDiv.innerHTML = `
            <button class="btn btn-sm btn-danger me-2" onclick="executeClearHistory()">
                <i class="fas fa-trash"></i> Да, очистить историю
            </button>
            <button class="btn btn-sm btn-secondary" onclick="cancelClearHistory()">
                <i class="fas fa-times"></i> Отмена
            </button>
        `;
        aiChatBody.appendChild(confirmDiv);

        aiChatBody.scrollTop = aiChatBody.scrollHeight;
    }

    // Глобальные функции для подтверждения очистки
    window.executeClearHistory = function() {
        // Удаляем кнопки подтверждения
        const confirmDiv = document.querySelector('.confirm-clear-history');
        if (confirmDiv) {
            confirmDiv.remove();
        }

        clearChatHistory();
    }

    window.cancelClearHistory = function() {
        // Удаляем кнопки подтверждения
        const confirmDiv = document.querySelector('.confirm-clear-history');
        if (confirmDiv) {
            confirmDiv.remove();
        }

        appendMessageToChat('Очистка истории отменена! 👍', 'ai', true);
    }

    // Interactive Tour Functions (остаются модальными)
    function initializeTourElements() {
        const modalElement = document.getElementById('interactiveTourModal');
        if (modalElement) {
            interactiveTourModal = new bootstrap.Modal(modalElement);
        }
        tourModalBody = document.getElementById('tourModalBody');
        tourStepNumberSpan = document.getElementById('tourStepNumber');
        nextTourStepBtn = document.getElementById('nextTourStepBtn');
        endTourBtn = document.getElementById('endTourBtn');
        closeTourModalBtn = document.getElementById('closeTourModalBtn');

        if (nextTourStepBtn && !nextButtonListenerAttached) {
            nextTourStepBtn.addEventListener('click', () => {
                if (currentTourStep >= MAX_TOUR_STEPS) {
                    completeTour();
                } else {
                    currentTourStep++;
                    if (currentTourStep <= MAX_TOUR_STEPS) {
                        showTourStep(currentTourStep);
                    } else {
                        completeTour();
                    }
                }
            });
            nextButtonListenerAttached = true;
        }
        if (endTourBtn) {
            endTourBtn.addEventListener('click', completeTour);
        }
        if (closeTourModalBtn) {
            closeTourModalBtn.addEventListener('click', completeTour);
        }
    }

    async function showTourStep(stepNumber) {
        if (!interactiveTourModal || !tourModalBody) return;

        tourModalBody.innerHTML = '<div class="text-center"><div class="spinner-border text-warning" role="status"></div></div>';
        interactiveTourModal.show();

        if (tourStepNumberSpan) {
            tourStepNumberSpan.textContent = stepNumber;
        }

        const requestData = {
            action_type: 'interactive_tour_step',
            step_number: stepNumber,
            user_info: {
                username: assistantContainer?.dataset.username || 'Гость'
            }
        };

        try {
            const response = await fetch('/assistant/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                tourModalBody.innerHTML = '<p class="text-danger">Ошибка загрузки шага тура</p>';
                return;
            }

            const responseData = await response.json();
            tourModalBody.innerHTML = responseData.response;

            if (typeof gsap !== 'undefined') {
                gsap.from(tourModalBody.children, {
                    opacity: 0,
                    y: 30,
                    stagger: 0.1,
                    duration: 0.5
                });
            }

            if (nextTourStepBtn) {
                if (stepNumber >= MAX_TOUR_STEPS) {
                    nextTourStepBtn.textContent = 'Завершить';
                } else {
                    nextTourStepBtn.textContent = 'Далее';
                }
            }

        } catch (error) {
            console.error('Ошибка:', error);
            tourModalBody.innerHTML = '<p class="text-danger">Произошла ошибка</p>';
        }
    }

    function completeTour() {
        if (interactiveTourModal) {
            interactiveTourModal.hide();
        }
        localStorage.setItem(getTourStorageKey(), 'true');
        currentTourStep = 1;
        showCompletionMessage();
    }

    function showCompletionMessage() {
        const message = document.createElement('div');
        message.className = 'completion-message';
        message.innerHTML = `
            <div class="completion-content">
                <i class="fas fa-trophy fa-3x text-warning mb-3"></i>
                <h4>Поздравляем! 🎉</h4>
                <p>Вы прошли тур по Chatty Orange!</p>
                <button class="btn btn-warning" onclick="this.parentElement.parentElement.remove()">Отлично!</button>
            </div>
        `;
        document.body.appendChild(message);

        if (typeof gsap !== 'undefined') {
            gsap.from(message, {
                scale: 0,
                opacity: 0,
                duration: 0.5,
                ease: "back.out(1.7)"
            });
        }
    }

    window.startInteractiveTour = function() {
        if (localStorage.getItem(getTourStorageKey()) === 'true') {
            if (confirm("Вы уже проходили тур. Хотите пройти его снова?")) {
                localStorage.removeItem(getTourStorageKey());
            } else {
                return false;
            }
        }
        currentTourStep = 1;
        initializeTourElements();
        showTourStep(currentTourStep);
        if (window.hideMenu) window.hideMenu();
        return false;
    }

    // Обработчики кликов по меню
    document.addEventListener('click', function(event) {
        if (event.target && event.target.id === 'startTourBtn') {
            event.preventDefault();
            window.startInteractiveTour();
        }

        if (event.target.matches('#showRecommendationsBtn') || event.target.closest('#showRecommendationsBtn')) {
            event.preventDefault();
            if (window.hideMenu) window.hideMenu();
            showRecommendations();
        }

        if (event.target.matches('#showProfileStatsBtn') || event.target.closest('#showProfileStatsBtn')) {
            event.preventDefault();
            if (window.hideMenu) window.hideMenu();
            showProfileStats();
        }

        if (event.target.matches('#showPostIdeasBtn') || event.target.closest('#showPostIdeasBtn')) {
            event.preventDefault();
            if (window.hideMenu) window.hideMenu();
            showPostIdeas();
        }
    });

    // Функции быстрого доступа
    async function showRecommendations() {
        window.showAIAssistant();
        currentActionType = 'subscription_recommendations';
        setTimeout(() => {
            sendChatMessage();
        }, 500);
    }

    async function showProfileStats() {
        window.showAIAssistant();
        currentActionType = 'analyze_profile';
        setTimeout(() => {
            sendChatMessage();
        }, 500);
    }

    async function showPostIdeas() {
        window.showAIAssistant();
        currentActionType = 'generate_post_ideas';
        setTimeout(() => {
            sendChatMessage();
        }, 500);
    }

    // Модальные окна (для правил и инструкций)
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

    // Инициализация
    initializeTourElements();

    // Автоматически открывать чат, если он был открыт ранее
    const chatWasOpen = localStorage.getItem(CHAT_OPEN_STATE_KEY);
    if (chatWasOpen === 'true') {
        if (typeof window.showAIAssistant === 'function') {
            // showAIAssistant сама вызовет createChatWidget, если нужно
            window.showAIAssistant();
        }
    }

    // Post Creation Helper
    const getPostSuggestionBtn = document.getElementById('getPostSuggestionBtn');
    const postSuggestionArea = document.getElementById('postSuggestionArea');

    if (getPostSuggestionBtn && postSuggestionArea) {
        getPostSuggestionBtn.addEventListener('click', async function() {
            let currentPostText = '';
            if (typeof CKEDITOR !== 'undefined' && CKEDITOR.instances.id_text) {
                currentPostText = CKEDITOR.instances.id_text.getData();
            } else {
                const plainTextArea = document.getElementById('id_text');
                if (plainTextArea) {
                    currentPostText = plainTextArea.value;
                }
            }

            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Думаю...';
            postSuggestionArea.style.display = 'none';

            const requestData = {
                action_type: 'post_creation_suggestion',
                current_text: currentPostText,
                user_info: {
                    username: assistantContainer?.dataset.username || 'Гость'
                }
            };

            try {
                const response = await fetch('/assistant/api/chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData)
                });

                if (!response.ok) {
                    postSuggestionArea.innerHTML = '<p class="text-danger">Произошла ошибка</p>';
                } else {
                    const responseData = await response.json();
                    postSuggestionArea.innerHTML = formatMessage(responseData.response);
                }
            } catch (error) {
                postSuggestionArea.innerHTML = '<p class="text-danger">Ошибка сети</p>';
            } finally {
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-lightbulb me-1"></i> Помощь ИИ с постом';
                postSuggestionArea.style.display = 'block';

                if (typeof gsap !== 'undefined') {
                    gsap.from(postSuggestionArea, {
                        opacity: 0,
                        height: 0,
                        duration: 0.3
                    });
                }
            }
        });
    }

    // Post Content Check
    const checkPostContentBtn = document.getElementById('checkPostContentBtn');
    const postCheckResultArea = document.getElementById('postCheckResultArea');

    if (checkPostContentBtn && postCheckResultArea) {
        checkPostContentBtn.addEventListener('click', async function() {
            let currentPostText = '';
            if (typeof CKEDITOR !== 'undefined' && CKEDITOR.instances.id_text) {
                currentPostText = CKEDITOR.instances.id_text.getData();
            } else {
                const plainTextArea = document.getElementById('id_text');
                if (plainTextArea) {
                    currentPostText = plainTextArea.value;
                }
            }

            if (!currentPostText.trim()) {
                postCheckResultArea.innerHTML = '<p class="text-warning">Введите текст для проверки</p>';
                postCheckResultArea.style.display = 'block';
                return;
            }

            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Проверяю...';

            const requestData = {
                action_type: 'check_post_content',
                user_input: currentPostText,
                user_info: {
                    username: assistantContainer?.dataset.username || 'Гость'
                }
            };

            try {
                const response = await fetch('/assistant/api/chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData)
                });

                if (!response.ok) {
                    postCheckResultArea.innerHTML = '<p class="text-danger">Ошибка проверки</p>';
                } else {
                    const responseData = await response.json();
                    postCheckResultArea.innerHTML = formatMessage(responseData.response);

                    if (responseData.response.includes('✅')) {
                        postCheckResultArea.className = 'mt-2 p-3 border rounded alert-success';
                    } else {
                        postCheckResultArea.className = 'mt-2 p-3 border rounded alert-warning';
                    }
                }
            } catch (error) {
                postCheckResultArea.innerHTML = '<p class="text-danger">Ошибка сети</p>';
            } finally {
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-shield-alt me-1"></i> Проверить текст';
                postCheckResultArea.style.display = 'block';
            }
        });
    }

    // Проверка для новых пользователей
    if (!localStorage.getItem('chattyOrangeReturningUser')) {
        setTimeout(() => {
            if (!localStorage.getItem(getTourStorageKey())) {
                showWelcomeMessage();
            }
        }, 3000);
        localStorage.setItem('chattyOrangeReturningUser', 'true');
    }

    function showWelcomeMessage() {
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-popup';
        welcomeDiv.innerHTML = `
            <div class="welcome-content">
                <img src="/static/images/orange.png" alt="Orange" style="width: 50px;">
                <p>Привет! Я Апельсиновый Помощник! 🍊</p>
                <p>Хочешь я покажу тебе, как пользоваться сайтом?</p>
                <button class="btn btn-warning btn-sm" onclick="window.startInteractiveTour(); this.parentElement.parentElement.remove();">
                    Да, покажи!
                </button>
                <button class="btn btn-outline-secondary btn-sm" onclick="this.parentElement.parentElement.remove();">
                    Позже
                </button>
            </div>
        `;
        document.body.appendChild(welcomeDiv);

        if (typeof gsap !== 'undefined') {
            gsap.from(welcomeDiv, {
                y: 100,
                opacity: 0,
                duration: 0.5,
                ease: "back.out(1.7)"
            });
        }
    }
});