import telebot
from telebot.types import ReplyKeyboardRemove

from config import BOT_TOKEN, CHANNEL_USERNAME, MESSAGES
from database import db
from keyboards import *
from utils import *

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Хранилище данных пользователей
user_sessions = {}

# Проверка подписки
def check_subscription(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

# ========== ОБРАБОТЧИКИ СООБЩЕНИЙ ==========

@bot.message_handler(commands=['start'])
def start(message):
    if not check_subscription(message.from_user.id):
        bot.send_message(message.chat.id, 
                        MESSAGES["not_subscribed"] + f"\n{CHANNEL_USERNAME}", 
                        reply_markup=subscription_keyboard())
        return
    
    show_main_menu(message.chat.id, message.from_user.first_name)

def show_main_menu(chat_id, first_name=None):
    greeting = MESSAGES["welcome"]
    if first_name:
        greeting = f"🎌 Привет, {first_name}!\n{greeting}"
    
    bot.send_message(chat_id, greeting, reply_markup=main_menu_keyboard())

# Поиск аниме
@bot.message_handler(func=lambda message: message.text == "🔍 Поиск аниме")
def search_anime(message):
    msg = bot.send_message(message.chat.id, "🔍 Введите название аниме:", 
                          reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_search)

def process_search(message):
    try:
        search_query = message.text.strip()
        if not search_query:
            bot.send_message(message.chat.id, "❌ Введите название аниме для поиска.")
            return
        
        results = db.search_anime(search_query)
        
        if results:
            bot.send_message(message.chat.id, 
                           f"🔍 Найдено аниме по запросу '{search_query}':",
                           reply_markup=anime_list_keyboard(results))
        else:
            bot.send_message(message.chat.id, MESSAGES["anime_not_found"])
            show_main_menu(message.chat.id)
            
    except Exception as e:
        bot.send_message(message.chat.id, MESSAGES["error"])
        print(f"Ошибка поиска: {e}")

# Популярное аниме
@bot.message_handler(func=lambda message: message.text == "📊 Популярное")
def popular_anime(message):
    # Берем первые 5 аниме из базы как популярные
    popular_list = list(db.data.items())[:5]
    
    if popular_list:
        bot.send_message(message.chat.id, "🔥 Популярное аниме:",
                        reply_markup=anime_list_keyboard(popular_list))
    else:
        bot.send_message(message.chat.id, "📊 Список популярного аниме пуст.")

# История просмотров
@bot.message_handler(func=lambda message: message.text == "📚 История просмотров")
def watch_history(message):
    user_id = message.from_user.id
    history = user_sessions.get(user_id, {}).get('history', [])
    
    if not history:
        bot.send_message(message.chat.id, "📚 История просмотров пуста.")
        return
    
    # Реализация истории просмотров может быть добавлена позже
    bot.send_message(message.chat.id, "📚 Функция истории в разработке...")

# ========== CALLBACK ОБРАБОТЧИКИ ==========

@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription_callback(call):
    if check_subscription(call.from_user.id):
        show_main_menu(call.message.chat.id, call.from_user.first_name)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ Вы еще не подписались на канал!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('select_episode:'))
def select_episode_callback(call):
    anime_id = call.data.split(':')[1]
    anime = db.get_anime(anime_id)
    
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
    anime = db.get_anime(anime_id)
    episode_data = db.get_episode(anime_id, episode)
    
    if not anime or not episode_data:
        bot.answer_callback_query(call.id, "❌ Данные не найдены!")
        return
    
    dubs = episode_data.get('dubs', {})
    
    if not dubs:
        bot.answer_callback_query(call.id, "❌ Озвучки не найдены!")
        return
    
    bot.edit_message_text(format_episode_info(anime['title'], episode, episode_data),
                         call.message.chat.id,
                         call.message.message_id,
                         reply_mup=dubs_keyboard(anime_id, episode, dubs))

@bot.callback_query_handler(func=lambda call: call.data.startswith('dub:'))
def select_quality_callback(call):
    _, anime_id, episode, dub_name = call.data.split(':')
    anime = db.get_anime(anime_id)
    episode_data = db.get_episode(anime_id, episode)
    
    if not anime or not episode_data:
        bot.answer_callback_query(call.id, "❌ Данные не найдены!")
        return
    
    dub_data = episode_data.get('dubs', {}).get(dub_name, {})
    qualities = dub_data.get('quality', {})
    
    if not qualities:
        bot.answer_callback_query(call.id, "❌ Качества не найдены!")
        return
    
    dub_display = get_dub_display_name(dub_name)
    
    bot.edit_message_text(f"🎬 {anime['title']} - Серия {episode}\n"
                         f"🎙️ Озвучка: {dub_display}\nВыберите качество:",
                         call.message.chat.id,
                         call.message.message_id,
                         reply_markup=quality_keyboard(anime_id, episode, dub_name, qualities))

@bot.callback_query_handler(func=lambda call: call.data.startswith('quality:'))
def send_video_callback(call):
    _, anime_id, episode, dub_name, quality = call.data.split(':')
    anime = db.get_anime(anime_id)
    episode_data = db.get_episode(anime_id, episode)
    
    if not anime or not episode_data:
        bot.answer_callback_query(call.id, "❌ Данные не найдены!")
        return
    
    video_url = episode_data.get('dubs', {}).get(dub_name, {}).get('quality', {}).get(quality)
    
    if not video_url:
        bot.answer_callback_query(call.id, "❌ Ссылка на видео не найдена!")
        return
    
    dub_display = get_dub_display_name(dub_name)
    
    try:
        # Сохраняем в историю
        user_id = call.from_user.id
        if user_id not in user_sessions:
            user_sessions[user_id] = {'history': []}
        
        history_record = f"{anime_id}:{episode}:{dub_name}:{quality}"
        user_sessions[user_id]['history'].insert(0, history_record)
        user_sessions[user_id]['history'] = user_sessions[user_id]['history'][:10]
        
        # Отправляем видео
        bot.send_video(call.message.chat.id,
                      video_url,
                      caption=f"🎬 {anime['title']} - Серия {episode}\n"
                             f"🎙️ Озвучка: {dub_display}\n"
                             f"📹 Качество: {quality}",
                      reply_markup=main_menu_keyboard())
        
    except Exception as e:
        bot.send_message(call.message.chat.id, 
                        "❌ Ошибка при загрузке видео. Попробуйте позже.")
        print(f"Ошибка отправки видео: {e}")

# Навигация назад
@bot.callback_query_handler(func=lambda call: call.data.startswith('back_to_anime:'))
def back_to_anime_callback(call):
    anime_id = call.data.split(':')[1]
    anime = db.get_anime(anime_id)
    
    if anime:
        bot.edit_message_text(format_anime_info(anime),
                            call.message.chat.id,
                            call.message.message_id,
                            reply_markup=anime_actions_keyboard(anime_id))
    else:
        bot.answer_callback_query(call.id, "❌ Аниме не найдено!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('info:'))
def anime_info_callback(call):
    anime_id = call.data.split(':')[1]
    anime = db.get_anime(anime_id)
    
    if anime:
        bot.edit_message_text(format_anime_info(anime),
                            call.message.chat.id,
                            call.message.message_id,
                            reply_markup=anime_actions_keyboard(anime_id))
    else:
        bot.answer_callback_query(call.id, "❌ Аниме не найдено!")

@bot.callback_query_handler(func=lambda call: call.data == "search_another")
def search_another_callback(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    search_anime(call.message)

if __name__ == "__main__":
    print("🤖 Бот запущен...")
    bot.polling(none_stop=True)
