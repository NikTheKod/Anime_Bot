import os
from dotenv import load_dotenv

load_dotenv()

# Настройки бота
BOT_TOKEN = os.getenv('BOT_TOKEN', '8281639128:AAEwpmH5OPPHA-5RtD3mG6208Sw2VMSQCWI')
CHANNEL_USERNAME = "@animevid_online"
ADMIN_IDS = [5109664392]  # Замените на ваш ID

# Настройки базы данных
DATABASE_FILE = "anime_data.json"

# Сообщения
MESSAGES = {
    "welcome": "🎌 Добро пожаловать в аниме бот!",
    "not_subscribed": "📢 Для использования бота необходимо подписаться на канал!",
    "anime_not_found": "❌ Аниме не найдено. Попробуйте другое название.",
    "error": "❌ Произошла ошибка. Попробуйте позже."
}
