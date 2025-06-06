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
    const assistantContainer = document.querySelector('.assistant-container');

    // Кнопки действий
    const aiFaqBtn = document.getElementById('aiFaqBtn');
    const aiFeatureBtn = document.getElementById('aiFeatureBtn');
    const aiProfileBtn = document.getElementById('aiProfileBtn');
    const aiIdeasBtn = document.getElementById('aiIdeasBtn');
    let currentActionType = 'general_chat';

    // Interactive Tour Elements
    let currentTourStep = 1;
    const MAX_TOUR_STEPS = 4;
    let interactiveTourModal = null;
    let tourModalBody = null;
    let tourStepNumberSpan = null;
    let nextTourStepBtn = null;
    let endTourBtn = null;
    let closeTourModalBtn = null;

    // Создаем расширенное меню
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

                // Добавляем обработчики для меню
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

    // Показать меню
    function showMenu() {
        if (!assistant) return;

        createMenu();
        if (!menu) return;

        isMenuOpen = true;
        menu.classList.add('show');

        // Анимация помощника
        if (typeof gsap !== 'undefined') {
            gsap.to(assistantImage, {
                scale: 1.1,
                rotation: -10,
                duration: 0.3
            });
        }
    }

    // Скрыть меню
    function hideMenu() {
        if (menu && isMenuOpen) {
            isMenuOpen = false;
            menu.classList.remove('show');

            // Возврат помощника в исходное состояние
            if (typeof gsap !== 'undefined') {
                gsap.to(assistantImage, {
                    scale: 1,
                    rotation: 0,
                    duration: 0.3
                });
            }
        }
    }

    // Проверка и скрытие меню
    function checkAndHideMenu() {
        setTimeout(() => {
            if (!isMouseOverAssistant && !isMouseOverMenu && isMenuOpen) {
                hideMenu();
            }
        }, 100);
    }

    // Глобальная функция скрытия меню
    window.hideMenu = hideMenu;

    // Обработчики событий для помощника
    if (assistantImage) {
        // Клик для переключения меню
        assistantImage.addEventListener('click', function(e) {
            e.stopPropagation();
            if (isMenuOpen) {
                hideMenu();
            } else {
                showMenu();
            }
        });

        // Наведение мыши
        assistantImage.addEventListener('mouseenter', function() {
            isMouseOverAssistant = true;
            if (!isMenuOpen) {
                showMenu();
            }
        });

        assistantImage.addEventListener('mouseleave', function() {
            isMouseOverAssistant = false;
            checkAndHideMenu();
        });
    }

    // Закрытие меню при клике вне его
    document.addEventListener('click', function(e) {
        if (isMenuOpen && assistant && !assistant.contains(e.target)) {
            hideMenu();
        }
    });

    // --- AI Assistant Chat Functions ---
    window.showAIAssistant = function() {
        if (aiChatBody) {
            aiChatBody.innerHTML = '';
            appendMessageToChat('Привет! 👋 Я твой Апельсиновый Помощник! Чем могу помочь сегодня?', 'ai');

            // Показываем быстрые кнопки
            appendQuickActions();
        }
        if (assistantBootstrapModal) {
            assistantBootstrapModal.show();
        }
        if (window.hideMenu) window.hideMenu();
        return false;
    }

    function appendQuickActions() {
        const quickActionsDiv = document.createElement('div');
        quickActionsDiv.className = 'quick-actions mt-3';
        quickActionsDiv.innerHTML = `
            <div class="d-flex flex-wrap gap-2">
                <button class="btn btn-sm btn-outline-warning quick-action" data-action="help">
                    <i class="fas fa-question-circle"></i> Помощь
                </button>
                <button class="btn btn-sm btn-outline-info quick-action" data-action="tour">
                    <i class="fas fa-route"></i> Тур
                </button>
                <button class="btn btn-sm btn-outline-success quick-action" data-action="ideas">
                    <i class="fas fa-lightbulb"></i> Идеи
                </button>
                <button class="btn btn-sm btn-outline-primary quick-action" data-action="stats">
                    <i class="fas fa-chart-line"></i> Статистика
                </button>
            </div>
        `;
        aiChatBody.appendChild(quickActionsDiv);

        // Обработчики для быстрых действий
        quickActionsDiv.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', function() {
                const action = this.dataset.action;
                handleQuickAction(action);
            });
        });
    }

    function handleQuickAction(action) {
        switch(action) {
            case 'help':
                currentActionType = 'faq';
                aiChatMessageInput.value = "Как создать пост?";
                sendChatMessage();
                break;
            case 'tour':
                window.startInteractiveTour();
                break;
            case 'ideas':
                currentActionType = 'generate_post_ideas';
                sendChatMessage();
                break;
            case 'stats':
                currentActionType = 'analyze_profile';
                sendChatMessage();
                break;
        }
    }

    function appendMessageToChat(message, sender) {
        if (!aiChatBody) return;

        const messageDiv = document.createElement('div');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'ai-message');

        if (sender === 'ai-thinking') {
            messageDiv.classList.remove('ai-message');
            messageDiv.classList.add('thinking');
        }

        // Поддержка форматирования
        const formattedMessage = formatMessage(message);
        messageDiv.innerHTML = formattedMessage;

        aiChatBody.appendChild(messageDiv);
        aiChatBody.scrollTop = aiChatBody.scrollHeight;

        // Анимация появления
        gsap.from(messageDiv, {
            opacity: 0,
            y: 20,
            duration: 0.3
        });
    }

    function formatMessage(message) {
        // Базовое форматирование
        let formatted = message
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/__(.*?)__/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');

        // Преобразование эмодзи в более крупный размер
        formatted = formatted.replace(/([\u{1F300}-\u{1F9FF}])/gu, '<span class="emoji">$1</span>');

        return formatted;
    }

    async function sendChatMessage() {
        if (!aiChatMessageInput && currentActionType === 'general_chat') return;

        const messageText = aiChatMessageInput ? aiChatMessageInput.value.trim() : '';

        if (messageText && currentActionType === 'general_chat') {
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

        // Показываем анимацию загрузки
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
            appendMessageToChat(responseData.response, 'ai');

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

    // Обработчики для кнопок действий
    if (aiFaqBtn) {
        aiFaqBtn.addEventListener('click', function() {
            currentActionType = 'faq';
            aiChatMessageInput.value = "Вопрос: ";
            aiChatMessageInput.focus();
            this.classList.add('active');
        });
    }

    if (aiFeatureBtn) {
        aiFeatureBtn.addEventListener('click', function() {
            currentActionType = 'feature_explanation';
            aiChatMessageInput.value = "Функция: ";
            aiChatMessageInput.focus();
            this.classList.add('active');
        });
    }

    // --- Interactive Tour Functions ---
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

        if (nextTourStepBtn) {
            nextTourStepBtn.addEventListener('click', () => {
                currentTourStep++;
                showTourStep(currentTourStep);
            });
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

            // Анимация контента
            gsap.from(tourModalBody.children, {
                opacity: 0,
                y: 30,
                stagger: 0.1,
                duration: 0.5
            });

            if (stepNumber >= MAX_TOUR_STEPS) {
                nextTourStepBtn.textContent = 'Завершить';
                nextTourStepBtn.onclick = completeTour;
            } else {
                nextTourStepBtn.textContent = 'Далее';
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
        localStorage.setItem('chattyOrangeTourCompleted', 'true');
        currentTourStep = 1;

        // Показываем поздравление
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

        gsap.from(message, {
            scale: 0,
            opacity: 0,
            duration: 0.5,
            ease: "back.out(1.7)"
        });
    }

    window.startInteractiveTour = function() {
        if (localStorage.getItem('chattyOrangeTourCompleted') === 'true') {
            if (confirm("Вы уже проходили тур. Хотите пройти его снова?")) {
                localStorage.removeItem('chattyOrangeTourCompleted');
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
        // Тур
        if (event.target && event.target.id === 'startTourBtn') {
            event.preventDefault();
            window.startInteractiveTour();
        }

        // Рекомендации
        if (event.target.matches('#showRecommendationsBtn') || event.target.closest('#showRecommendationsBtn')) {
            event.preventDefault();
            if (window.hideMenu) window.hideMenu();
            showRecommendations();
        }

        // Статистика профиля
        if (event.target.matches('#showProfileStatsBtn') || event.target.closest('#showProfileStatsBtn')) {
            event.preventDefault();
            if (window.hideMenu) window.hideMenu();
            showProfileStats();
        }

        // Идеи для постов
        if (event.target.matches('#showPostIdeasBtn') || event.target.closest('#showPostIdeasBtn')) {
            event.preventDefault();
            if (window.hideMenu) window.hideMenu();
            showPostIdeas();
        }
    });

    // Функция показа рекомендаций
    async function showRecommendations() {
        window.showAIAssistant();
        currentActionType = 'subscription_recommendations';
        setTimeout(() => {
            sendChatMessage();
        }, 500);
    }

    // Функция показа статистики
    async function showProfileStats() {
        window.showAIAssistant();
        currentActionType = 'analyze_profile';
        setTimeout(() => {
            sendChatMessage();
        }, 500);
    }

    // Функция показа идей для постов
    async function showPostIdeas() {
        window.showAIAssistant();
        currentActionType = 'generate_post_ideas';
        setTimeout(() => {
            sendChatMessage();
        }, 500);
    }

    // Модальные окна
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

    // --- Post Creation Helper ---
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

                // Анимация появления
                gsap.from(postSuggestionArea, {
                    opacity: 0,
                    height: 0,
                    duration: 0.3
                });
            }
        });
    }

    // --- Post Content Check ---
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

                    // Добавляем цветовую индикацию
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
            if (!localStorage.getItem('chattyOrangeTourCompleted')) {
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

        gsap.from(welcomeDiv, {
            y: 100,
            opacity: 0,
            duration: 0.5,
            ease: "back.out(1.7)"
        });
    }
});