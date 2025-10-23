from config import MESSAGES

def get_dub_display_name(dub_name):
    """Получение красивого названия озвучки"""
    dub_names = {
        "anilibria": "AniLibria",
        "animevost": "AnimeVost",
        "shiza": "Shiza Project",
        "cuba77": "Cuba77",
        "animedia": "AniMedia",
        "jacker": "Jacker",
        "kansai": "Kansai"
    }
    return dub_names.get(dub_name, dub_name)

def format_anime_info(anime_data):
    """Форматирование информации об аниме"""
    title = anime_data.get('title', 'Без названия')
    description = anime_data.get('description', 'Описание отсутствует')
    episodes_count = len(anime_data.get('episodes', {}))
    
    return f"🎬 {title}\n\n📖 {description}\n\n📺 Серий: {episodes_count}"

def format_episode_info(anime_title, episode_number, episode_data):
    """Форматирование информации о серии"""
    episode_title = episode_data.get('title', f'Серия {episode_number}')
    dubs_count = len(episode_data.get('dubs', {}))
    
    return f"🎬 {anime_title}\n📺 Серия {episode_number}: {episode_title}\n🎙️ Озвучек: {dubs_count}"
