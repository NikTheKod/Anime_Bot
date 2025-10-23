from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton, 
                          ReplyKeyboardMarkup, KeyboardButton)
from config import CHANNEL_USERNAME
from utils import get_dub_display_name

def main_menu_keyboard():
    """Главное меню"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔍 Поиск аниме"))
    markup.add(KeyboardButton("📊 Популярное"), KeyboardButton("🎬 Новинки"))
    markup.add(KeyboardButton("📚 История просмотров"))
    return markup

def subscription_keyboard():
    """Клавиатура для подписки на канал"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📺 Подписаться на канал", 
                                   url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
    markup.add(InlineKeyboardButton("✅ Я подписался", 
                                   callback_data="check_subscription"))
    return markup

def anime_list_keyboard(anime_list):
    """Клавиатура со списком аниме"""
    markup = InlineKeyboardMarkup()
    
    for anime_id, anime_data in anime_list:
        title = anime_data.get('title', 'Без названия')
        markup.add(InlineKeyboardButton(f"🎬 {title}", 
                                       callback_data=f"select_episode:{anime_id}"))
    
    return markup

def anime_actions_keyboard(anime_id):
    """Клавиатура действий с аниме"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📺 Выбрать серию", 
                                   callback_data=f"select_episode:{anime_id}"))
    markup.add(InlineKeyboardButton("ℹ️ Информация", 
                                   callback_data=f"info:{anime_id}"))
    markup.add(InlineKeyboardButton("🔍 Поиск другого", 
                                   callback_data="search_another"))
    return markup

def episodes_keyboard(anime_id, episodes):
    """Клавиатура выбора серии"""
    markup = InlineKeyboardMarkup()
    
    # Сортируем серии по номеру
    sorted_episodes = sorted(episodes.items(), key=lambda x: int(x[0]))
    
    row = []
    for ep_num, ep_data in sorted_episodes[-12:]:  # Последние 12 серий
        row.append(InlineKeyboardButton(f"{ep_num}", 
                                       callback_data=f"episode:{anime_id}:{ep_num}"))
        if len(row) == 3:  # 3 кнопки в ряд
            markup.add(*row)
            row = []
    
    if row:
        markup.add(*row)
    
    markup.add(InlineKeyboardButton("🔙 Назад", 
                                   callback_data=f"back_to_anime:{anime_id}"))
    return markup

def dubs_keyboard(anime_id, episode_number, dubs):
    """Клавиатура выбора озвучки"""
    markup = InlineKeyboardMarkup()
    
    for dub_name in dubs.keys():
        display_name = get_dub_display_name(dub_name)
        markup.add(InlineKeyboardButton(f"🎙️ {display_name}", 
                                       callback_data=f"dub:{anime_id}:{episode_number}:{dub_name}"))
    
    markup.add(InlineKeyboardButton("🔙 Назад", 
                                   callback_data=f"episode:{anime_id}:{episode_number}"))
    return markup

def quality_keyboard(anime_id, episode_number, dub_name, qualities):
    """Клавиатура выбора качества"""
    markup = InlineKeyboardMarkup()
    
    for quality in qualities.keys():
        markup.add(InlineKeyboardButton(f"📹 {quality}", 
                                       callback_data=f"quality:{anime_id}:{episode_number}:{dub_name}:{quality}"))
    
    markup.add(InlineKeyboardButton("🔙 Назад", 
                                   callback_data=f"dub:{anime_id}:{episode_number}:{dub_name}"))
    return markup
