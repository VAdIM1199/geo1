# logic.py
import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

class DB_Map():
    def __init__(self, database):
        self.database = database
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.database)
        with conn:
            # Создаем таблицу с дополнительной информацией о городах
            conn.execute('''CREATE TABLE IF NOT EXISTS cities_info (
                            city TEXT PRIMARY KEY,
                            country TEXT,
                            population INTEGER,
                            density REAL,
                            timezone REAL
                        )''')
            conn.commit()

    def get_country_cities(self, country):
        """Получить все города страны"""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT city FROM cities_info WHERE country=?", (country,))
            return [row[0] for row in cursor.fetchall()]

    def get_cities_by_density(self, min_density):
        """Получить города с плотностью выше указанной"""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT city FROM cities_info WHERE density>=?", (min_density,))
            return [row[0] for row in cursor.fetchall()]

    def get_city_info(self, city_name):
        """Получить полную информацию о городе"""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT country, population, density, timezone 
                            FROM cities_info WHERE city=?''', (city_name,))
            row = cursor.fetchone()
            if row:
                return {
                    'country': row[0],
                    'population': row[1],
                    'density': row[2],
                    'timezone': f"+{row[3]}" if row[3] >= 0 else row[3]
                }
            return None

    def get_city_timezone(self, city_name):
        """Получить часовой пояс города"""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT timezone FROM cities_info WHERE city=?", (city_name,))
            row = cursor.fetchone()
            return row[0] if row else None

    def create_graph(self, path, cities, color='blue'):
        """Отрисовка городов на карте"""
        fig = plt.figure(figsize=(10, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        # Базовая карта с континентами и океанами
        ax.stock_img()
        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        
        # Добавляем города
        for city in cities:
            coords = self.get_coordinates(city)
            if coords:
                lat, lon = coords
                plt.plot(lon, lat, marker='o', color=color, markersize=8,
                        transform=ccrs.Geodetic())
                plt.text(lon + 2, lat + 2, city, transform=ccrs.Geodetic())
        
        plt.savefig(path)
        plt.close()

    # ... остальные существующие методы ...

if __name__ == "__main__":
    db = DB_Map(DATABASE)