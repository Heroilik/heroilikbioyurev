<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Семен Юрьев | Чат с ботом</title>
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,600;14..32,700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(145deg, #1a1f2e 0%, #2a2f44 100%);
            color: #1e1f2a;
            line-height: 1.6;
            padding: 2rem 1.5rem;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* Карточка профиля */
        .profile-card {
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(20px);
            border-radius: 48px;
            padding: 2.8rem 2.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 30px 60px -20px rgba(0, 20, 40, 0.5);
        }

        .hero {
            display: flex;
            gap: 2.5rem;
            align-items: center;
            flex-wrap: wrap;
        }

        .photo-frame {
            width: 180px;
            height: 180px;
            border-radius: 50%;
            background: linear-gradient(135deg, #ffb6c1, #ffdab9);
            padding: 6px;
        }

        .photo-placeholder {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            overflow: hidden;
        }

        .photo-placeholder img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .hero-text h1 {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(145deg, #23253b, #3f3f6c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .tags {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }

        .tag {
            background: rgba(255,255,255,0.7);
            padding: 0.5rem 1.5rem;
            border-radius: 40px;
            font-weight: 500;
        }

        .tag i {
            color: #6574c7;
            margin-right: 8px;
        }

        /* Чат */
        .chat-card {
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(20px);
            border-radius: 48px;
            padding: 2rem;
            margin-bottom: 2rem;
        }

        .chat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid rgba(255,255,255,0.5);
        }

        .chat-title {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .chat-title i {
            font-size: 2rem;
            color: #667eea;
        }

        .connection-status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 30px;
            background: white;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }

        .status-dot.connected {
            background: #4caf50;
            box-shadow: 0 0 10px #4caf50;
        }

        .status-dot.disconnected {
            background: #f44336;
        }

        /* Сообщения */
        .messages {
            height: 400px;
            overflow-y: auto;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .message {
            max-width: 70%;
            padding: 1rem;
            border-radius: 20px;
            animation: fadeIn 0.3s;
        }

        .user-message {
            align-self: flex-end;
            background: #667eea;
            color: white;
            border-bottom-right-radius: 5px;
        }

        .bot-message {
            align-self: flex-start;
            background: white;
            color: #333;
            border-bottom-left-radius: 5px;
        }

        .message-time {
            font-size: 0.7rem;
            opacity: 0.7;
            margin-top: 0.3rem;
        }

        /* Ввод */
        .input-area {
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 2px solid rgba(255,255,255,0.5);
        }

        .message-input {
            flex: 1;
            padding: 1rem 1.5rem;
            border: none;
            border-radius: 40px;
            font-size: 1rem;
            background: white;
            outline: none;
        }

        .send-button {
            width: 60px;
            height: 60px;
            border-radius: 30px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            cursor: pointer;
            transition: 0.3s;
        }

        .send-button:hover {
            transform: scale(1.1);
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
        }

        .send-button i {
            font-size: 1.5rem;
        }

        /* Кнопки действий */
        .action-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }

        .action-btn {
            padding: 0.8rem 1.5rem;
            border: none;
            border-radius: 30px;
            background: white;
            cursor: pointer;
            font-weight: 500;
            transition: 0.2s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .action-btn i {
            color: #667eea;
        }

        /* Социальные кнопки */
        .social-links {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 2rem;
            flex-wrap: wrap;
        }

        .social-btn {
            width: 52px;
            height: 52px;
            border-radius: 30px;
            background: white;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #2f3b6b;
            font-size: 1.6rem;
            text-decoration: none;
            transition: 0.2s;
        }

        .social-btn:hover {
            background: #667eea;
            color: white;
            transform: translateY(-3px);
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Профиль -->
        <div class="profile-card">
            <div class="hero">
                <div class="photo-frame">
                    <div class="photo-placeholder">
                        <img src="https://randomuser.me/api/portraits/men/44.jpg" alt="Семен">
                    </div>
                </div>
                <div class="hero-text">
                    <h1>Семен Юрьев</h1>
                    <div class="tags">
                        <span class="tag"><i class="fas fa-brush"></i> Лоутабер</span>
                        <span class="tag"><i class="fas fa-briefcase"></i> Деловой человек</span>
                        <span class="tag"><i class="fas fa-map-pin"></i> Томск</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Чат -->
        <div class="chat-card">
            <div class="chat-header">
                <div class="chat-title">
                    <i class="fab fa-telegram"></i>
                    <h2>Чат с ботом</h2>
                </div>
                <div class="connection-status" id="connectionStatus">
                    <span class="status-dot disconnected" id="statusDot"></span>
                    <span id="statusText">Проверка соединения...</span>
                </div>
            </div>

            <!-- Сообщения -->
            <div class="messages" id="messages">
                <div class="message bot-message">
                    👋 Привет! Я бот Семена. Напиши мне что-нибудь!
                    <div class="message-time">только что</div>
                </div>
            </div>

            <!-- Ввод сообщения -->
            <div class="input-area">
                <input type="text" class="message-input" id="messageInput" 
                       placeholder="Введите сообщение..." onkeypress="if(event.key==='Enter') sendMessage()">
                <button class="send-button" onclick="sendMessage()">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>

            <!-- Кнопки действий -->
            <div class="action-buttons">
                <button class="action-btn" onclick="loadHistory()">
                    <i class="fas fa-history"></i> История
                </button>
                <button class="action-btn" onclick="checkBotStatus()">
                    <i class="fas fa-sync-alt"></i> Статус бота
                </button>
                <a href="https://t.me/WhitesharkT" target="_blank" class="action-btn">
                    <i class="fab fa-telegram"></i> Открыть в Telegram
                </a>
            </div>
        </div>

        <!-- Социальные сети -->
        <div class="social-links">
            <a href="https://t.me/WhitesharkT" class="social-btn" target="_blank"><i class="fab fa-telegram-plane"></i></a>
            <a href="#" class="social-btn" onclick="alert('VK')"><i class="fab fa-vk"></i></a>
            <a href="#" class="social-btn" onclick="alert('YouTube')"><i class="fab fa-youtube"></i></a>
            <a href="https://steamcommunity.com/profiles/76561199683308328" class="social-btn" target="_blank"><i class="fab fa-steam"></i></a>
        </div>
    </div>

    <script>
        // ====================== НАСТРОЙКИ ======================
        const API_URL = 'http://localhost:5000/api';  // Адрес вашего сервера
        let userId = null;
        let username = 'web_user_' + Math.floor(Math.random() * 1000);
        
        // ====================== ГЕНЕРАЦИЯ USER ID ======================
        function generateUserId() {
            // Пробуем получить из localStorage
            let id = localStorage.getItem('userId');
            if (!id) {
                id = Date.now() + Math.floor(Math.random() * 1000000);
                localStorage.setItem('userId', id);
            }
            userId = id;
            return id;
        }

        // ====================== ПРОВЕРКА СТАТУСА ======================
        async function checkBotStatus() {
            try {
                const response = await fetch(`${API_URL}/status`);
                const data = await response.json();
                
                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');
                
                if (response.ok) {
                    statusDot.className = 'status-dot connected';
                    statusText.textContent = `✅ Бот онлайн (${data.bot})`;
                    addBotMessage('✅ Бот подключен и работает!');
                } else {
                    statusDot.className = 'status-dot disconnected';
                    statusText.textContent = '❌ Бот не отвечает';
                }
            } catch (error) {
                document.getElementById('statusDot').className = 'status-dot disconnected';
                document.getElementById('statusText').textContent = '❌ Сервер недоступен';
                addBotMessage('❌ Не удалось подключиться к серверу. Убедитесь, что Python бот запущен.');
            }
        }

        // ====================== ОТПРАВКА СООБЩЕНИЯ ======================
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Очищаем input
            input.value = '';
            
            // Генерируем userId если нужно
            if (!userId) generateUserId();
            
            // Добавляем сообщение пользователя в чат
            addUserMessage(message);
            
            try {
                // Отправляем на сервер
                const response = await fetch(`${API_URL}/send`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_id: parseInt(userId),
                        message: message,
                        username: username
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Добавляем ответ бота
                    addBotMessage(data.response);
                } else {
                    addBotMessage('❌ Ошибка отправки: ' + (data.error || 'Неизвестная ошибка'));
                }
            } catch (error) {
                addBotMessage('❌ Ошибка соединения с сервером');
                console.error('Error:', error);
            }
        }

        // ====================== ЗАГРУЗКА ИСТОРИИ ======================
        async function loadHistory() {
            if (!userId) generateUserId();
            
            try {
                const response = await fetch(`${API_URL}/history/${userId}`);
                const history = await response.json();
                
                if (history.length > 0) {
                    // Очищаем чат
                    document.getElementById('messages').innerHTML = '';
                    
                    // Добавляем историю в обратном порядке
                    history.reverse().forEach(msg => {
                        if (msg.message) {
                            addUserMessage(msg.message, false);
                        }
                        if (msg.response) {
                            addBotMessage(msg.response, false);
                        }
                    });
                    
                    addBotMessage('📜 История загружена');
                } else {
                    addBotMessage('📭 История пуста');
                }
            } catch (error) {
                addBotMessage('❌ Не удалось загрузить историю');
            }
        }

        // ====================== ДОБАВЛЕНИЕ СООБЩЕНИЙ ======================
        function addUserMessage(text, save = true) {
            const messagesDiv = document.getElementById('messages');
            const time = new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
            
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message user-message';
            messageDiv.innerHTML = `
                ${text}
                <div class="message-time">${time}</div>
            `;
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function addBotMessage(text, save = true) {
            const messagesDiv = document.getElementById('messages');
            const time = new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
            
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot-message';
            messageDiv.innerHTML = `
                ${text}
                <div class="message-time">${time}</div>
            `;
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // ====================== ИНИЦИАЛИЗАЦИЯ ======================
        window.onload = function() {
            generateUserId();
            checkBotStatus();
            
            // Проверяем статус каждые 30 секунд
            setInterval(checkBotStatus, 30000);
        }
    </script>
</body>
</html>
