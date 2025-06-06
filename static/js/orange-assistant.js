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

    // Interactive Tour Elements
    let currentTourStep = 1;
    const MAX_TOUR_STEPS = 4; // Предположим, у нас 4 шага в туре
    let interactiveTourModal = null;
    let tourModalBody = null;
    let tourStepNumberSpan = null;
    let nextTourStepBtn = null;
    let endTourBtn = null;
    let closeTourModalBtn = null;


    // Создаем меню один раз при загрузке
    function createMenu() {
        if (!menu) {
            menu = document.createElement('div');
            menu.className = 'assistant-menu';
            menu.innerHTML = `
                <a href="#" onclick="return window.showRules()">Правила сайта</a>
                <a href="#" onclick="return window.showGuide()">Инструкция сайта</a>
                <a href="#" id="startTourBtn">Пройти тур по сайту</a>
                <a href="#" id="showRecommendationsBtn">Кого почитать?</a>
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

    // --- Interactive Tour Functions ---
    function initializeTourElements() {
        const modalElement = document.getElementById('interactiveTourModal');
        if (modalElement) {
            interactiveTourModal = new bootstrap.Modal(modalElement);
        }
        tourModalBody = document.getElementById('tourModalBody');
        tourStepNumberSpan = document.getElementById('tourStepNumber');
        nextTourStepBtn = document.getElementById('nextTourStepBtn');
        endTourBtn = document.getElementById('endTourBtn'); // Главная кнопка "Завершить тур"
        closeTourModalBtn = document.getElementById('closeTourModalBtn'); // Крестик в хедере модалки

        if (nextTourStepBtn) {
            nextTourStepBtn.addEventListener('click', () => {
                currentTourStep++;
                showTourStep(currentTourStep);
            });
        }
        if (endTourBtn) {
            endTourBtn.addEventListener('click', completeTour);
        }
        if (closeTourModalBtn) { // Также закрывает тур
            closeTourModalBtn.addEventListener('click', completeTour);
        }
        // Закрытие модального окна через data-bs-dismiss (например, клик вне модалки) также должно завершать тур
        if (modalElement) {
            modalElement.addEventListener('hidden.bs.modal', function () {
                // Если модальное окно было закрыто любым способом (кроме programmatic hide в completeTour),
                // и тур не был завершен через кнопку, засчитываем как завершение.
                // Чтобы избежать двойной установки localStorage, проверяем, открыто ли еще модальное окно (странно, но на всякий).
                // Более простой подход - completeTour будет вызван кнопками, а если пользователь закрыл иначе - тоже засчитать.
                // Флаг 'tourInProgress' мог бы помочь, но пока усложнит.
                // Просто вызовем completeTour, если он еще не был вызван.
                // Проверим, установлен ли уже флаг, чтобы не вызывать лишний раз, если completeTour уже отработал.
                if (localStorage.getItem('chattyOrangeTourCompleted') !== 'true') {
                    // Это условие может быть не всегда верным, если пользователь быстро кликает.
                    // Лучше, чтобы completeTour был идемпотентным или имел внутреннюю проверку.
                    // На данном этапе, просто вызываем. Если что, localStorage перезапишется тем же значением.
                     // completeTour(); // Это может вызывать show() снова, если неаккуратно.
                     // Вместо этого просто установим флаг, если он еще не установлен.
                     // Но правильнее, чтобы completeTour сам проверял и закрывал.
                     // Пока оставим так, что закрытие модалки любым способом = завершение тура.
                     localStorage.setItem('chattyOrangeTourCompleted', 'true');
                     console.log("Tour implicitly completed by closing modal.");
                }
            });
        }
    }

    async function showTourStep(stepNumber) {
        if (!interactiveTourModal || !tourModalBody || !tourStepNumberSpan || !nextTourStepBtn) {
            console.error("Элементы модального окна тура не найдены.");
            return;
        }

        tourModalBody.innerHTML = '<p>Загрузка информации о шаге...</p>';
        interactiveTourModal.show();
        if(tourStepNumberSpan) tourStepNumberSpan.textContent = stepNumber;

        const requestData = {
            action_type: 'interactive_tour_step',
            step_number: stepNumber,
            user_info: {
                username: assistantContainer && assistantContainer.dataset.username ? assistantContainer.dataset.username : 'anonymous'
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
                let errorDetail = response.statusText;
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.error || errorData.detail || errorDetail;
                } catch (e) { /* Do nothing */ }
                tourModalBody.innerHTML = `<p>Ошибка загрузки шага: ${errorDetail}</p>`;
                return;
            }

            const responseData = await response.json();
            tourModalBody.innerHTML = responseData.response.replace(/\n/g, '<br>');

            if (stepNumber >= MAX_TOUR_STEPS) {
                nextTourStepBtn.textContent = 'Завершить';
                // Можно было бы и скрыть кнопку "Далее" и оставить только "Завершить тур",
                // но смена текста тоже подойдет. При клике все равно вызовется completeTour, если currentTourStep станет > MAX_TOUR_STEPS.
                // Или явно перенаправить:
                nextTourStepBtn.onclick = completeTour; // Переназначаем действие кнопки
            } else {
                nextTourStepBtn.textContent = 'Далее';
                nextTourStepBtn.onclick = () => { // Возвращаем стандартное действие
                    currentTourStep++;
                    showTourStep(currentTourStep);
                };
            }

        } catch (error) {
            console.error('Ошибка при загрузке шага тура:', error);
            tourModalBody.innerHTML = '<p>Произошла ошибка при загрузке шага тура. Попробуйте позже.</p>';
        }
    }

    function completeTour() {
        if (interactiveTourModal) {
            interactiveTourModal.hide();
        }
        localStorage.setItem('chattyOrangeTourCompleted', 'true');
        console.log("Интерактивный тур завершен и сохранен в localStorage.");
        // Сбрасываем currentTourStep на случай, если пользователь захочет пройти тур снова (хотя сейчас он не сможет без очистки localStorage)
        currentTourStep = 1;
        // Восстанавливаем кнопку "Далее", если она была изменена
        if (nextTourStepBtn) {
            nextTourStepBtn.textContent = 'Далее';
            nextTourStepBtn.onclick = () => {
                currentTourStep++;
                showTourStep(currentTourStep);
            };
        }

        // Опционально: предлагаем показать рекомендации после завершения тура
        if (confirm("Тур завершен! Хотите посмотреть рекомендации интересных авторов?")) {
            // Убедимся, что модальное окно чата открыто и очищено
            if (window.showAIAssistant && typeof window.showAIAssistant === 'function') {
                 // Вызываем showAIAssistant так, чтобы он не добавлял стандартное приветствие, а подготовил чат
                if (aiChatBody) aiChatBody.innerHTML = ''; // Очищаем чат напрямую
                if (assistantBootstrapModal) assistantBootstrapModal.show(); // Показываем модалку
                // Не вызываем hideMenu здесь, т.к. showAIAssistant может его вызвать
            } else {
                 // Если showAIAssistant не определен глобально, пытаемся показать модалку напрямую
                 if (assistantBootstrapModal) assistantBootstrapModal.show();
            }
            // Добавляем сообщение о подборе и вызываем рекомендации
            if (aiChatBody) appendMessageToChat('Сейчас подберу для вас интересные профили...', 'ai-thinking');
            showSubscriptionRecommendations();
        }
    }

    window.startInteractiveTour = function() {
        if (localStorage.getItem('chattyOrangeTourCompleted') === 'true') {
            // Можно предложить пройти тур заново или просто ничего не делать
            // Для примера, просто выведем сообщение и не будем начинать
            if (confirm("Вы уже проходили тур. Хотите пройти его снова? (Это сбросит отметку о прохождении)")) {
                 localStorage.removeItem('chattyOrangeTourCompleted');
            } else {
                alert("Вы уже завершили интерактивный тур.");
                if (window.hideMenu) window.hideMenu();
                return false;
            }
        }
        console.log("Starting interactive tour");
        currentTourStep = 1; // Начинаем всегда с первого шага
        initializeTourElements(); // Инициализируем элементы модального окна (если еще не были)
        showTourStep(currentTourStep);
        if (window.hideMenu) window.hideMenu();
        return false; // для <a href="#">
    }

    // Добавляем обработчик для кнопки старта тура после создания меню
    // Это должно быть сделано так, чтобы #startTourBtn уже существовала.
    // Безопаснее всего это сделать после вызова createMenu() или делегировать событие.
    // Поскольку createMenu() вызывается в showMenu(), а showMenu() при наведении/клике,
    // то #startTourBtn может еще не существовать при первой загрузке DOMContentLoaded.
    // Решение: добавим слушатель на document и проверим target.
    document.addEventListener('click', function(event) {
        if (event.target && event.target.id === 'startTourBtn') {
            event.preventDefault(); // Предотвращаем стандартное действие ссылки
            window.startInteractiveTour();
        }
        // Обработчик для кнопки "Кого почитать?"
        if (event.target.matches('#showRecommendationsBtn') || event.target.closest('#showRecommendationsBtn')) {
            event.preventDefault();
            if (window.hideMenu) window.hideMenu();

            // Подготовка чата и показ модального окна ассистента
            if (aiChatBody) {
                aiChatBody.innerHTML = ''; // Очищаем предыдущие сообщения
                // Устанавливаем currentActionType в null или специальное значение, чтобы sendChatMessage не сработал,
                // если пользователь что-то введет и нажмет Enter до получения рекомендаций.
                // Либо просто не отображаем поле ввода для рекомендаций.
                // Пока просто очистим и покажем сообщение "думает".
                // Также отключаем поле ввода и кнопку отправки на время загрузки рекомендаций.
                if(aiChatMessageInput) aiChatMessageInput.disabled = true;
                if(aiSendMessageBtn) aiSendMessageBtn.disabled = true;
            }

            // Открываем модальное окно ассистента, если оно еще не открыто
            // Используем логику, похожую на showAIAssistant, но без стандартного приветствия
            if (assistantBootstrapModal && !assistantModalElement.classList.contains('show')) {
                 assistantBootstrapModal.show();
            }
            // Добавляем сообщение "думает" уже после возможного открытия модалки
            if (aiChatBody) appendMessageToChat('Подбираю для вас интересные профили...', 'ai-thinking');

            showSubscriptionRecommendations();
        }
    });

    // Инициализация элементов тура при загрузке страницы, если пользователь решит начать тур не через меню
    // (например, если бы была кнопка "Начать тур" где-то еще)
    // initializeTourElements(); // Вызовем один раз, чтобы элементы были готовы

    // Проверка, нужно ли автоматически предлагать тур (например, для новых пользователей)
    // Эту логику можно будет добавить позже. Сейчас тур запускается только через меню.
    // if (localStorage.getItem('chattyOrangeTourCompleted') !== 'true') {
    //     // Можно показать какой-то баннер или кнопку "Начать тур" более заметно
    // }


    // --- End Interactive Tour Functions ---


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

    // Инициализируем элементы тура один раз при загрузке DOM,
    // чтобы модальное окно было готово к использованию.
    initializeTourElements();

    // --- Post Creation Suggestion Functions ---
    const getPostSuggestionBtn = document.getElementById('getPostSuggestionBtn');
    const postSuggestionArea = document.getElementById('postSuggestionArea');
    // assistantContainer для user_info должен быть уже доступен глобально, если он определен ранее в скрипте.
    // const assistantContainer = document.querySelector('.assistant-container'); // Уже определен выше

    if (getPostSuggestionBtn && postSuggestionArea) {
        getPostSuggestionBtn.addEventListener('click', async function() {
            let currentPostText = '';
            // Убедимся, что CKEDITOR и его инстанс существуют
            if (typeof CKEDITOR !== 'undefined' && CKEDITOR.instances.id_text) {
                currentPostText = CKEDITOR.instances.id_text.getData();
            } else {
                console.warn('CKEditor instance for id_text not found. Trying fallback to textarea.');
                const plainTextArea = document.getElementById('id_text');
                if (plainTextArea) {
                    currentPostText = plainTextArea.value;
                } else {
                    console.error('Fallback textarea #id_text also not found.');
                    postSuggestionArea.innerHTML = '<p class="text-danger">Не удалось получить текст поста. Редактор не найден.</p>';
                    postSuggestionArea.style.display = 'block';
                    return;
                }
            }

            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Думаю...';
            postSuggestionArea.style.display = 'none'; // Сначала скрыть, потом показать с результатом
            postSuggestionArea.innerHTML = ''; // Очистка предыдущих подсказок

            const requestData = {
                action_type: 'post_creation_suggestion',
                current_text: currentPostText, // Используем current_text как ключ, как в views.py
                user_info: {
                    username: assistantContainer && assistantContainer.dataset.username ? assistantContainer.dataset.username : 'anonymous'
                }
            };

            try {
                const response = await fetch('/assistant/api/chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        // 'X-CSRFToken': getCsrfTokenValue() // TODO: Implement CSRF if needed
                    },
                    body: JSON.stringify(requestData)
                });

                if (!response.ok) {
                    let errorDetail = `Ошибка ${response.status}: ${response.statusText}`;
                    try {
                        const errorData = await response.json();
                        errorDetail = errorData.error || errorData.detail || errorDetail;
                    } catch (e) { /* Оставляем errorDetail как response.statusText */ }
                    postSuggestionArea.innerHTML = `<p class="text-danger">Ошибка от сервера: ${errorDetail}</p>`;
                } else {
                    const responseData = await response.json();
                    // Форматируем ответ ИИ, заменяя переносы строк на <br>
                    const formattedResponse = responseData.response.replace(/\n/g, '<br>');
                    postSuggestionArea.innerHTML = formattedResponse;
                }
            } catch (error) {
                console.error('Ошибка при запросе подсказки для поста:', error);
                postSuggestionArea.innerHTML = '<p class="text-danger">Сетевая ошибка или ошибка обработки ответа. Пожалуйста, проверьте консоль.</p>';
            } finally {
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-lightbulb me-1"></i> Помощь ИИ с постом';
                postSuggestionArea.style.display = 'block';
            }
        });
    }
    // --- End Post Creation Suggestion Functions ---

    // --- Subscription Recommendation Functions ---
    async function showSubscriptionRecommendations() {
        // Сообщение "думает" уже должно быть добавлено вызывающей функцией (из completeTour или из обработчика #showRecommendationsBtn)

        const requestData = {
            action_type: 'subscription_recommendations',
            user_info: {
                username: assistantContainer && assistantContainer.dataset.username ? assistantContainer.dataset.username : 'anonymous',
                // userId: assistantContainer && assistantContainer.dataset.userId ? assistantContainer.dataset.userId : null // Если нужно
            }
        };

        try {
            const response = await fetch('/assistant/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // 'X-CSRFToken': getCsrfToken() // TODO: если CSRF используется
                },
                body: JSON.stringify(requestData)
            });

            // Удаляем сообщение "думает"
            if (aiChatBody) {
                const thinkingMessage = aiChatBody.querySelector('.thinking'); // Ищем по классу 'thinking'
                if (thinkingMessage) {
                    aiChatBody.removeChild(thinkingMessage);
                }
            }

            if (!response.ok) {
                let errorDetail = response.statusText;
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.error || errorData.detail || errorDetail;
                } catch (e) { /* Оставляем errorDetail как есть */ }
                appendMessageToChat(`Ошибка при загрузке рекомендаций: ${errorDetail}`, 'ai');
            } else {
                const responseData = await response.json();
                appendMessageToChat(responseData.response, 'ai'); // Ответ ИИ уже должен быть отформатирован
            }
        } catch (error) {
            console.error('Ошибка при запросе рекомендаций подписок:', error);
            if (aiChatBody) {
                 const thinkingMessage = aiChatBody.querySelector('.thinking');
                 if (thinkingMessage) aiChatBody.removeChild(thinkingMessage);
            }
            appendMessageToChat('Сетевая ошибка или ошибка при обработке рекомендаций. Проверьте консоль.', 'ai');
        } finally {
            // Включаем обратно поле ввода и кнопку, если они были отключены
             if(aiChatMessageInput) aiChatMessageInput.disabled = false;
             if(aiSendMessageBtn) aiSendMessageBtn.disabled = false;
             // Можно также сбросить currentActionType, если это имеет смысл для общего чата
             // currentActionType = 'general_chat';
        }
    }
    // --- End Subscription Recommendation Functions ---

    // --- Post Content Check Functions ---
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
                } else {
                    console.error('CKEditor or fallback textarea #id_text not found for post content check.');
                    postCheckResultArea.innerHTML = '<p class="text-danger">Не удалось получить текст поста. Редактор не найден.</p>';
                    postCheckResultArea.style.display = 'block';
                    return;
                }
            }

            if (!currentPostText.trim()) {
                postCheckResultArea.innerHTML = '<p class="text-warning">Пожалуйста, введите текст для проверки.</p>';
                postCheckResultArea.style.display = 'block';
                // Также скроем область для предложений, если она была открыта
                if(postSuggestionArea) postSuggestionArea.style.display = 'none';
                return;
            }

            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Проверяю...';
            postCheckResultArea.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> Проверка текста по правилам...</p>'; // Предзагрузочное сообщение
            postCheckResultArea.style.display = 'block';
            // Скроем область для предложений, если она была открыта, чтобы не было двух одновременно
            if(postSuggestionArea) postSuggestionArea.style.display = 'none';


            const requestData = {
                action_type: 'check_post_content',
                user_input: currentPostText, // user_input используется для передачи текста поста
                user_info: {
                    username: assistantContainer && assistantContainer.dataset.username ? assistantContainer.dataset.username : 'anonymous'
                }
            };

            try {
                const response = await fetch('/assistant/api/chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        // 'X-CSRFToken': getCsrfToken() // TODO: если CSRF используется
                    },
                    body: JSON.stringify(requestData)
                });

                let resultHTML = '';
                if (!response.ok) {
                    let errorDetail = response.statusText;
                    try {
                        const errorData = await response.json();
                        errorDetail = errorData.error || errorData.detail || errorDetail;
                    } catch (e) { /* Оставляем errorDetail как есть */ }
                    resultHTML = `<p class="text-danger">Ошибка проверки: ${errorDetail}</p>`;
                } else {
                    const responseData = await response.json();
                    // Заменяем переносы строк на <br> для корректного отображения
                    resultHTML = responseData.response.replace(/\n/g, '<br>');
                }
                postCheckResultArea.innerHTML = resultHTML;

            } catch (error) {
                console.error('Ошибка при запросе проверки поста:', error);
                postCheckResultArea.innerHTML = '<p class="text-danger">Сетевая ошибка или ошибка обработки ответа при проверке. Проверьте консоль.</p>';
            } finally {
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-shield-alt me-1"></i> Проверить текст по правилам';
                postCheckResultArea.style.display = 'block';
            }
        });
    }
    // --- End Post Content Check Functions ---
});