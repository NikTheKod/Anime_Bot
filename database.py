import json
import os
from config import DATABASE_FILE

class Database:
    def __init__(self):
        self.data = self.load_data()
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def search_anime(self, query):
        """Поиск аниме по названию"""
        query = query.lower()
        results = []
        
        for anime_id, anime_data in self.data.items():
            title = anime_data.get('title', '').lower()
            if query in title or query in anime_id:
                results.append((anime_id, anime_data))
        
        return results
    
    def get_anime(self, anime_id):
        """Получение данных об аниме по ID"""
        return self.data.get(anime_id)
    
    def get_episode(self, anime_id, episode_number):
        """Получение данных о серии"""
        anime = self.get_anime(anime_id)
        if anime and episode_number in anime.get('episodes', {}):
            return anime['episodes'][episode_number]
        return None
    
    def add_anime(self, anime_id, title, description=""):
        """Добавление нового аниме (для админов)"""
        if anime_id not in self.data:
            self.data[anime_id] = {
                "title": title,
                "description": description,
                "episodes": {}
            }
            self.save_data()
            return True
        return False

# Глобальный экземпляр базы данных
db = Database()
