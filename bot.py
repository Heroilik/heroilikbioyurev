"""
Telegram бот с поддержкой Mini App и базой данных
Один файл - всё включено
"""

import logging
import sqlite3
import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import parse_qs

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

# ====================== НАСТРОЙКИ ======================
TOKEN = "8790386520:AAEC1xExtvQ3rAFXlTweqepsuJcF1og8e6c"  # Замените на токен вашего бота
ADMIN_IDS = [1631589431]  # Замените на ID администраторов
DB_PATH = "chat_history.db"
WEBAPP_URL = "http://127.0.0.1:5500/"  # Замените на URL вашего сайта

# Состояния для ConversationHandler
MAIN_MENU, CHATTING, ADMIN_PANEL = range(3)

# ====================== РАБОТА С БАЗОЙ ДАННЫХ ======================

def init_database():
    """Инициализация базы данных SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registered_at TIMESTAMP,
            last_activity TIMESTAMP,
            is_admin INTEGER DEFAULT 0,
            is_blocked INTEGER DEFAULT 0
        )
    ''')
    
    # Таблица истории сообщений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            response TEXT,
            timestamp TIMESTAMP,
            is_from_admin INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Таблица для хранения контекста диалога
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            user_id INTEGER PRIMARY KEY,
            context TEXT,
            last_message_time TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Таблица для данных из Mini App
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS webapp_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            data TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def register_user(user_id: int, username: str, first_name: str, last_name: str):
    """Регистрация нового пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, registered_at, last_activity)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name, datetime.now(), datetime.now()))
    
    conn.commit()
    conn.close()

def update_user_activity(user_id: int):
    """Обновление времени последней активности"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users SET last_activity = ? WHERE user_id = ?
    ''', (datetime.now(), user_id))
    
    conn.commit()
    conn.close()

def save_message(user_id: int, message: str, response: str = None, is_from_admin: bool = False):
    """Сохранение сообщения в базу данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO messages (user_id, message, response, timestamp, is_from_admin)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, message, response, datetime.now(), 1 if is_from_admin else 0))
    
    conn.commit()
    conn.close()

def save_webapp_data(user_id: int, data: dict):
    """Сохранение данных из Mini App"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO webapp_data (user_id, data, timestamp)
        VALUES (?, ?, ?)
    ''', (user_id, json.dumps(data), datetime.now()))
    
    conn.commit()
    conn.close()

def get_user_history(user_id: int, limit: int = 10) -> List[Dict]:
    """Получение истории сообщений пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT message, response, timestamp FROM messages 
        WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?
    ''', (user_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {"message": row[0], "response": row[1], "timestamp": row[2]}
        for row in rows
    ]

def save_context(user_id: int, context: str):
    """Сохранение контекста диалога"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO conversations (user_id, context, last_message_time)
        VALUES (?, ?, ?)
    ''', (user_id, context, datetime.now()))
    
    conn.commit()
    conn.close()

def get_context(user_id: int) -> Optional[str]:
    """Получение контекста диалога"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT context FROM conversations WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    return row[0] if row else None

def get_all_users() -> List[Dict]:
    """Получение списка всех пользователей для админа"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, username, first_name, last_name, registered_at, last_activity, is_blocked
        FROM users ORDER BY last_activity DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "user_id": row[0],
            "username": row[1],
            "first_name": row[2],
            "last_name": row[3],
            "registered_at": row[4],
            "last_activity": row[5],
            "is_blocked": row[6]
        }
        for row in rows
    ]

def is_user_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user_id in ADMIN_IDS

def is_user_blocked(user_id: int) -> bool:
    """Проверка, заблокирован ли пользователь"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT is_blocked FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    return row[0] == 1 if row else False

def block_user(user_id: int):
    """Блокировка пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET is_blocked = 1 WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()

def unblock_user(user_id: int):
    """Разблокировка пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET is_blocked = 0 WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()

# ====================== ВАЛИДАЦИЯ ДАННЫХ ИЗ MINI APP ======================

def validate_telegram_init_data(init_data: str, bot_token: str) -> dict:
    """
    Валидация данных инициализации от Telegram Mini App
    
    Args:
        init_data: Строка initData из Telegram.WebApp.initData
        bot_token: Токен бота
        
    Returns:
        dict: Данные пользователя если валидация успешна, иначе None
    """
    try:
        # Парсим данные
        parsed_data = parse_qs(init_data)
        
        # Извлекаем хэш
        received_hash = parsed_data.get('hash', [None])[0]
        if not received_hash:
            return None
        
        # Удаляем хэш из данных для проверки
        parsed_data.pop('hash', None)
        
        # Сортируем ключи и создаем строку для проверки
        data_check_string = '\n'.join(
            f"{key}={value[0]}" 
            for key, value in sorted(parsed_data.items())
        )
        
        # Создаем секретный ключ
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=bot_token.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        # Вычисляем ожидаемый хэш
        expected_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Сравниваем хэши
        if expected_hash != received_hash:
            return None
        
        # Парсим данные пользователя
        user_data = {}
        if 'user' in parsed_data:
            user_data = json.loads(parsed_data['user'][0])
        
        return {
            'user': user_data,
            'auth_date': parsed_data.get('auth_date', [None])[0],
            'query_id': parsed_data.get('query_id', [None])[0]
        }
    except Exception as e:
        logging.error(f"Ошибка валидации init_data: {e}")
        return None

# ====================== ОБРАБОТЧИКИ КОМАНД ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Регистрируем пользователя
    register_user(
        user.id,
        user.username,
        user.first_name,
        user.last_name
    )
    
    # Создаем клавиатуру главного меню с кнопкой Mini App
    keyboard = [
        [InlineKeyboardButton(
            "🌐 Открыть Mini App", 
            web_app=WebAppInfo(url=f"{WEBAPP_URL}?user_id={user.id}")
        )],
        [InlineKeyboardButton("💬 Начать чат", callback_data="start_chat")],
        [InlineKeyboardButton("📜 Моя история", callback_data="my_history")],
        [InlineKeyboardButton("ℹ️ О боте", callback_data="about")]
    ]
    
    # Добавляем админ-панель, если пользователь админ
    if is_user_admin(user.id):
        keyboard.append([InlineKeyboardButton("👑 Админ панель", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"Я бот с Mini App. Выберите действие или откройте веб-приложение:",
        reply_markup=reply_markup
    )
    
    return MAIN_MENU

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == "start_chat":
        # Начинаем чат
        await query.edit_message_text(
            "💬 Режим чата активирован!\n\n"
            "Просто отправляйте сообщения, и я буду отвечать.\n"
            "Чтобы вернуться в меню, отправьте /menu"
        )
        return CHATTING
    
    elif query.data == "my_history":
        # Показываем историю сообщений
        history = get_user_history(user_id)
        
        if not history:
            await query.edit_message_text(
                "📭 У вас пока нет истории сообщений.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")
                ]])
            )
        else:
            history_text = "📜 Ваша история сообщений:\n\n"
            for msg in history[:5]:
                history_text += f"👤 Вы: {msg['message'][:50]}...\n"
                if msg['response']:
                    history_text += f"🤖 Бот: {msg['response'][:50]}...\n"
                history_text += f"🕐 {msg['timestamp']}\n\n"
            
            await query.edit_message_text(
                history_text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")
                ]])
            )
        return MAIN_MENU
    
    elif query.data == "about":
        await query.edit_message_text(
            "ℹ️ О боте\n\n"
            "Версия: 2.0\n"
            "Разработчик: @your_username\n\n"
            "Этот бот поддерживает Mini App для удобного взаимодействия.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")
            ]])
        )
        return MAIN_MENU
    
    elif query.data == "admin_panel":
        if not is_user_admin(user_id):
            await query.edit_message_text("⛔ У вас нет доступа к админ-панели.")
            return MAIN_MENU
        
        # Показываем админ-панель
        users = get_all_users()
        
        keyboard = [
            [InlineKeyboardButton("👥 Список пользователей", callback_data="admin_users")],
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("📨 Рассылка", callback_data="admin_broadcast")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")]
        ]
        
        await query.edit_message_text(
            f"👑 Админ панель\n\n"
            f"Всего пользователей: {len(users)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ADMIN_PANEL
    
    elif query.data == "back_to_menu":
        # Возвращаемся в главное меню
        keyboard = [
            [InlineKeyboardButton(
                "🌐 Открыть Mini App", 
                web_app=WebAppInfo(url=f"{WEBAPP_URL}?user_id={user_id}")
            )],
            [InlineKeyboardButton("💬 Начать чат", callback_data="start_chat")],
            [InlineKeyboardButton("📜 Моя история", callback_data="my_history")],
            [InlineKeyboardButton("ℹ️ О боте", callback_data="about")]
        ]
        
        if is_user_admin(user_id):
            keyboard.append([InlineKeyboardButton("👑 Админ панель", callback_data="admin_panel")])
        
        await query.edit_message_text(
            "Главное меню:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return MAIN_MENU
    
    # Обработчики для админ-панели
    elif query.data == "admin_users":
        if not is_user_admin(user_id):
            return MAIN_MENU
        
        users = get_all_users()
        users_text = "👥 Список пользователей:\n\n"
        
        for user in users[:10]:
            status = "🚫" if user['is_blocked'] else "✅"
            users_text += f"{status} ID: {user['user_id']}\n"
            users_text += f"   Имя: {user['first_name']} {user['last_name'] or ''}\n"
            users_text += f"   Username: @{user['username'] or 'нет'}\n"
            users_text += f"   Последняя активность: {user['last_activity']}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔍 Заблокировать пользователя", callback_data="admin_block")],
            [InlineKeyboardButton("🔓 Разблокировать", callback_data="admin_unblock")],
            [InlineKeyboardButton("◀️ Назад", callback_data="admin_panel")]
        ]
        
        await query.edit_message_text(
            users_text + "Всего пользователей: " + str(len(users)),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ADMIN_PANEL
    
    elif query.data == "admin_stats":
        if not is_user_admin(user_id):
            return MAIN_MENU
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM messages")
        active_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM webapp_data")
        total_webapp_actions = cursor.fetchone()[0]
        
        conn.close()
        
        await query.edit_message_text(
            f"📊 Статистика бота:\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"💬 Всего сообщений: {total_messages}\n"
            f"✨ Активных пользователей: {active_users}\n"
            f"🌐 Действий в Mini App: {total_webapp_actions}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Назад", callback_data="admin_panel")
            ]])
        )
        return ADMIN_PANEL
    
    elif query.data == "admin_broadcast":
        if not is_user_admin(user_id):
            return MAIN_MENU
        
        context.user_data['broadcast_mode'] = True
        await query.edit_message_text(
            "📨 Режим рассылки\n\n"
            "Отправьте сообщение, которое хотите разослать всем пользователям.\n"
            "Для отмены отправьте /cancel",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Отмена", callback_data="admin_panel")
            ]])
        )
        return ADMIN_PANEL
    
    return MAIN_MENU

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик сообщений в режиме чата"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Проверяем, не заблокирован ли пользователь
    if is_user_blocked(user_id):
        await update.message.reply_text("⛔ Вы заблокированы в этом боте.")
        return CHATTING
    
    # Обновляем активность
    update_user_activity(user_id)
    
    # Получаем контекст диалога
    context_data = get_context(user_id)
    
    # Простые ответы для демонстрации
    responses = {
        "привет": "И тебе привет! 👋",
        "как дела": "У меня всё отлично! А у тебя?",
        "что делаешь": "Общаюсь с тобой 😊",
        "пока": "До свидания! Возвращайся в меню через /menu",
    }
    
    # Поиск ответа в словаре
    response_text = "Я тебя слушаю. Расскажи что-нибудь ещё!"
    for key, response in responses.items():
        if key in message_text.lower():
            response_text = response
            break
    
    # Сохраняем сообщение и ответ в БД
    save_message(user_id, message_text, response_text)
    
    # Сохраняем контекст
    save_context(user_id, f"Последнее сообщение: {message_text[:50]}")
    
    # Отправляем ответ
    await update.message.reply_text(response_text)
    
    return CHATTING

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /menu для возврата в меню"""
    return await start(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена текущего действия"""
    await update.message.reply_text(
        "Действие отменено. Используйте /start для возврата в меню."
    )
    return ConversationHandler.END

async def admin_broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик рассылки для админа"""
    if not context.user_data.get('broadcast_mode', False):
        return MAIN_MENU
    
    user_id = update.effective_user.id
    if not is_user_admin(user_id):
        return MAIN_MENU
    
    message_text = update.message.text
    
    # Получаем всех пользователей
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE is_blocked = 0")
    users = cursor.fetchall()
    conn.close()
    
    # Отправляем сообщение всем
    success_count = 0
    for user in users:
        try:
            await context.bot.send_message(
                user[0],
                f"📢 Рассылка от администратора:\n\n{message_text}"
            )
            success_count += 1
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение пользователю {user[0]}: {e}")
    
    context.user_data['broadcast_mode'] = False
    
    await update.message.reply_text(
        f"✅ Рассылка завершена!\n"
        f"Отправлено {success_count} из {len(users)} пользователям."
    )
    
    return MAIN_MENU

# ====================== ЗАПУСК БОТА ======================

def main():
    """Главная функция запуска бота"""
    # Инициализируем базу данных
    init_database()
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Создаем ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(button_handler),
                CommandHandler('menu', menu_command)
            ],
            CHATTING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler),
                CommandHandler('menu', menu_command)
            ],
            ADMIN_PANEL: [
                CallbackQueryHandler(button_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_broadcast_handler),
                CommandHandler('menu', menu_command),
                CommandHandler('cancel', cancel)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # Запускаем бота
    print(f"Бот запущен... Mini App URL: {WEBAPP_URL}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()