import telebot
import json
import os
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton, 
                          ReplyKeyboardMarkup, KeyboardButton)

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = "8281639128:AAEwpmH5OPPHA-5RtD3mG6208Sw2VMSQCWI"  # ЗАМЕНИТЕ на ваш токен от @BotFather
CHANNEL_USERNAME = "@animevid_online"

# ========== БАЗА ДАННЫХ ==========
def load_anime_data():
    """Загрузка данных об аниме"""
    try:
        with open('anime_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # Возвращаем тестовые данные если файла нет
        return {
            "attack_on_titan": {
                "title": "Атака Титанов",
                "description": "История о выживании человечества против титанов",
                "episodes": {
                    "1": {
                        "title": "Тому день, когда я тебе крикнул: Смирись",
                        "dubs": {
                            "anilibria": {
                                "quality": {
                                    "720p": "https://example.com/aot1_720p.mp4",
                                    "1080p": "https://example.com/aot1_1080p.mp4"
                                }
                            },
                            "animevost": {
                                "quality": {
                                    "720p": "https://example.com/aot1_720p_av.mp4"
                                }
                            }
                        }
                    },
                    "2": {
                        "title": "В тот день",
                        "dubs": {
                            "anilibria": {
                                "quality": {
                                    "720p": "https://example.com/aot2_720p.mp4"
                                }
                            }
                        }
                    }
                }
            },
            "demon_slayer": {
                "title": "Истребитель демонов", 
                "description": "Тандзиро становится истребителем демонов чтобы спасти сестру",
                "episodes": {
                    "1": {
                        "title": "Жестокость",
                        "dubs": {
                            "anilibria": {
                                "quality": {
                                    "720p": "https://example.com/ds1_720p.mp4"
                                }
                            }
                        }
                    }
                }
            }
        }

def save_anime_data(data):
    """Сохранение данных об аниме"""
    with open('anime_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Загружаем данные
anime_data = load_anime_data()

# ========== УТИЛИТЫ ==========
def get_dub_display_name(dub_name):
    """Красивые названия озвучек"""
    dub_names = {
        "anilibria": "AniLibria",
        "animevost": "AnimeVost", 
        "shiza": "Shiza Project",
        "cuba77": "Cuba77",
        "animedia": "AniMedia"
    }
    return dub_names.get(dub_name, dub_name)

# ========== КЛАВИАТУРЫ ==========
def main_menu_keyboard():
    """Главное меню"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔍 Поиск аниме"))
    markup.add(KeyboardButton("📊 Популярное"), KeyboardButton("🎬 Новинки"))
    return markup

def anime_actions_keyboard(anime_id):
    """Кнопки для аниме"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📺 Выбрать серию", callback_data=f"select_episode:{anime_id}"))
    markup.add(InlineKeyboardButton("ℹ️ Информация", callback_data=f"info:{anime_id}"))
    return markup

def episodes_keyboard(anime_id, episodes):
    """Кнопки серий"""
    markup = InlineKeyboardMarkup()
    
    # Сортируем серии
    sorted_episodes = sorted(episodes.items(), key=lambda x: int(x[0]))
    
    # Показываем последние 12 серий
    for ep_num, ep_data in sorted_episodes[-12:]:
        markup.add(InlineKeyboardButton(f"Серия {ep_num}", 
                                      callback_data=f"episode:{anime_id}:{ep_num}"))
    
    markup.add(InlineKeyboardButton("🔙 Назад", callback_data=f"back_to_anime:{anime_id}"))
    return markup

def dubs_keyboard(anime_id, episode_number, dubs):
    """Кнопки озвучек"""
    markup = InlineKeyboardMarkup()
    
    for dub_name in dubs.keys():
        display_name = get_dub_display_name(dub_name)
        markup.add(InlineKeyboardButton(f"🎙️ {display_name}", 
                                      callback_data=f"dub:{anime_id}:{episode_number}:{dub_name}"))
    
    markup.add(InlineKeyboardButton("🔙 Назад", 
                                  callback_data=f"episode:{anime_id}:{episode_number}"))
    return markup

def quality_keyboard(anime_id, episode_number, dub_name, qualities):
    """Кнопки качества"""
    markup = InlineKeyboardMarkup()
    
    for quality in qualities.keys():
        markup.add(InlineKeyboardButton(f"📹 {quality}", 
                                      callback_data=f"quality:{anime_id}:{episode_number}:{dub_name}:{quality}"))
    
    markup.add(InlineKeyboardButton("🔙 Назад", 
                                  callback_data=f"dub:{anime_id}:{episode_number}:{dub_name}"))
    return markup

# ========== ИНИЦИАЛИЗАЦИЯ БОТА ==========
bot = telebot.TeleBot(BOT_TOKEN)

# ========== ПРОВЕРКА ПОДПИСКИ (ОТКЛЮЧЕНА) ==========
def check_subscription(user_id):
    """ВРЕМЕННО ОТКЛЮЧЕНА ПРОВЕРКА ПОДПИСКИ"""
    return True

# ========== ОБРАБОТЧИКИ ==========
@bot.message_handler(commands=['start'])
def start(message):
    show_main_menu(message.chat.id, message.from_user.first_name)

def show_main_menu(chat_id, first_name=None):
    greeting = "🎌 Добро пожаловать в аниме бот!"
    if first_name:
        greeting = f"🎌 Привет, {first_name}!\n{greeting}"
    
    bot.send_message(chat_id, greeting, reply_markup=main_menu_keyboard())

@bot.message_handler(func=lambda message: message.text == "🔍 Поиск аниме")
def search_anime(message):
    msg = bot.send_message(message.chat.id, "🔍 Введите название аниме:")
    bot.register_next_step_handler(msg, process_search)

def process_search(message):
    search_query = message.text.lower().strip()
    results = []
    
    # Простой поиск
    for anime_id, anime_data in anime_data.items():
        title = anime_data.get('title', '').lower()
        if search_query in title or search_query in anime_id:
            results.append((anime_id, anime_data))
    
    if results:
        # Показываем первое найденное аниме
        anime_id, anime = results[0]
        show_anime_info(message.chat.id, anime_id, anime)
    else:
        bot.send_message(message.chat.id, "❌ Аниме не найдено. Попробуйте другое название.")
        show_main_menu(message.chat.id)

def show_anime_info(chat_id, anime_id, anime=None):
    if not anime:
        anime = anime_data.get(anime_id)
    
    if not anime:
        bot.send_message(chat_id, "❌ Аниме не найдено.")
        return
    
    title = anime.get('title', 'Без названия')
    description = anime.get('description', 'Описание отсутствует')
    episodes_count = len(anime.get('episodes', {}))
    
    text = f"🎬 {title}\n\n📖 {description}\n\n📺 Серий: {episodes_count}"
    bot.send_message(chat_id, text, reply_markup=anime_actions_keyboard(anime_id))

@bot.message_handler(func=lambda message: message.text == "📊 Популярное")
def popular_anime(message):
    # Показываем первые 5 аниме как популярные
    popular_list = list(anime_data.items())[:5]
    
    if popular_list:
        for anime_id, anime in popular_list:
            show_anime_info(message.chat.id, anime_id, anime)
    else:
        bot.send_message(message.chat.id, "📊 Список популярного аниме пуст.")

# ========== CALLBACK ОБРАБОТЧИКИ ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith('select_episode:'))
def select_episode_callback(call):
    anime_id = call.data.split(':')[1]
    anime = anime_data.get(anime_id)
    
    if not anime:
        bot.answer_callback_query(call.id, "❌ Аниме не найдено!")
        return
    
    episodes = anime.get('episodes', {})
    
    if not episodes:
        bot.answer_callback_query(call.id, "❌ Серии не найдены!")
        return
    
    bot.edit_message_text(f"🎬 {anime['title']}\nВыберите серию:",
                         call.message.chat.id,
                         call.message.message_id,
                         reply_markup=episodes_keyboard(anime_id, episodes))

@bot.callback_query_handler(func=lambda call: call.data.startswith('episode:'))
def select_dub_callback(call):
    _, anime_id, episode = call.data.split(':')
    anime = anime_data.get(anime_id)
    
    if not anime:
        bot.answer_callback_query(call.id, "❌ Аниме не найдено!")
        return
    
    episode_data = anime.get('episodes', {}).get(episode)
    if not episode_data:
        bot.answer_callback_query(call.id, "❌ Серия не найдена!")
        return
    
    dubs = episode_data.get('dubs', {})
    
    if not dubs:
        bot.answer_callback_query(call.id, "❌ Озвучки не найдены!")
        return
    
    episode_title = episode_data.get('title', f'Серия {episode}')
    bot.edit_message_text(f"🎬 {anime['title']} - {episode_title}\nВыберите озвучку:",
                         call.message.chat.id,
                         call.message.message_id,
                         reply_markup=dubs_keyboard(anime_id, episode, dubs))

@bot.callback_query_handler(func=lambda call: call.data.startswith('dub:'))
def select_quality_callback(call):
    _, anime_id, episode, dub_name = call.data.split(':')
    anime = anime_data.get(anime_id)
    
    if not anime:
        bot.answer_callback_query(call.id, "❌ Аниме не найдено!")
        return
    
    episode_data = anime.get('episodes', {}).get(episode)
    if not episode_data:
        bot.answer_callback_query(call.id, "❌ Серия не найдена!")
        return
    
    dub_data = episode_data.get('dubs', {}).get(dub_name, {})
    qualities = dub_data.get('quality', {})
    
    if not qualities:
        bot.answer_callback_query(call.id, "❌ Качества не найдены!")
        return
    
    dub_display = get_dub_display_name(dub_name)
    episode_title = episode_data.get('title', f'Серия {episode}')
    
    bot.edit_message_text(f"🎬 {anime['title']} - {episode_title}\n"
                         f"🎙️ Озвучка: {dub_display}\nВыберите качество:",
                         call.message.chat.id,
                         call.message.message_id,
                         reply_markup=quality_keyboard(anime_id, episode, dub_name, qualities))

@bot.callback_query_handler(func=lambda call: call.data.startswith('quality:'))
def send_video_callback(call):
    _, anime_id, episode, dub_name, quality = call.data.split(':')
    anime = anime_data.get(anime_id)
    
    if not anime:
        bot.answer_callback_query(call.id, "❌ Аниме не найдено!")
        return
    
    episode_data = anime.get('episodes', {}).get(episode)
    if not episode_data:
        bot.answer_callback_query(call.id, "❌ Серия не найдена!")
        return
    
    video_url = episode_data.get('dubs', {}).get(dub_name, {}).get('quality', {}).get(quality)
    
    if not video_url or video_url.startswith("https://example.com"):
        bot.send_message(call.message.chat.id,
                        f"🎬 {anime['title']} - Серия {episode}\n"
                        f"🎙️ Озвучка: {get_dub_display_name(dub_name)}\n"
                        f"📹 Качество: {quality}\n\n"
                        "❌ Ссылка на видео не настроена. Нужно добавить реальные ссылки в anime_data.json")
        return
    
    dub_display = get_dub_display_name(dub_name)
    episode_title = episode_data.get('title', f'Серия {episode}')
    
    try:
        # Пробуем отправить видео
        bot.send_video(call.message.chat.id,
                      video_url,
                      caption=f"🎬 {anime['title']} - {episode_title}\n"
                             f"🎙️ Озвучка: {dub_display}\n"
                             f"📹 Качество: {quality}")
        
    except Exception as e:
        # Если не получилось отправить видео, отправляем ссылку
        bot.send_message(call.message.chat.id,
                        f"🎬 {anime['title']} - {episode_title}\n"
                        f"🎙️ Озвучка: {dub_display}\n"
                        f"📹 Качество: {quality}\n\n"
                        f"🔗 Ссылка на видео: {video_url}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('back_to_anime:'))
def back_to_anime_callback(call):
    anime_id = call.data.split(':')[1]
    anime = anime_data.get(anime_id)
    
    if anime:
        show_anime_info(call.message.chat.id, anime_id, anime)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ Аниме не найдено!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('info:'))
def anime_info_callback(call):
    anime_id = call.data.split(':')[1]
    show_anime_info(call.message.chat.id, anime_id)

# ========== ЗАПУСК БОТА ==========
if __name__ == "__main__":
    print("🤖 Бот запущен! Проверка подписки отключена.")
    print("📝 Не забудьте заменить YOUR_BOT_TOKEN_HERE на реальный токен!")
    bot.polling(none_stop=True)