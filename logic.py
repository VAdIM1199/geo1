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
        self.create_user_table()

    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return True
            return False

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city
                            FROM users_cities
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            return [row[0] for row in cursor.fetchall()]

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities
                            WHERE city = ?''', (city_name,))
            return cursor.fetchone()

    def create_graph(self, path, cities, color='red'):
        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())

        ax.add_feature(cfeature.LAND, facecolor='#f0e68c')  
        ax.add_feature(cfeature.OCEAN, facecolor='#add8e6')  
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)  
        ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5) 
        ax.add_feature(cfeature.LAKES, facecolor='#add8e6')  
        ax.add_feature(cfeature.RIVERS, linewidth=0.5)  
        
        ax.set_global()
        
        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lng = coordinates
                plt.plot([lng], [lat], color=color, linewidth=1, marker='o', markersize=8, 
                         transform=ccrs.Geodetic())
                plt.text(lng + 3, lat + 12, city, color=color, fontsize=10,
                        horizontalalignment='left', transform=ccrs.Geodetic())

        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()

    def draw_distance(self, city1, city2, path, color='green'):
        city1_coords = self.get_coordinates(city1)
        city2_coords = self.get_coordinates(city2)
        
        if not city1_coords or not city2_coords:
            return False
            
        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        ax.add_feature(cfeature.LAND, facecolor='#f0e68c')
        ax.add_feature(cfeature.OCEAN, facecolor='#add8e6')
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
        ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
        ax.set_global()

        plt.plot([city1_coords[1], city2_coords[1]], 
                 [city1_coords[0], city2_coords[0]], 
                 color=color, linewidth=2, marker='o', markersize=8,
                 transform=ccrs.Geodetic())
        plt.text(city1_coords[1] + 3, city1_coords[0] + 12, city1, 
                color=color, fontsize=10, transform=ccrs.Geodetic())
        plt.text(city2_coords[1] + 3, city2_coords[0] + 12, city2, 
                color=color, fontsize=10, transform=ccrs.Geodetic())
        
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        return True