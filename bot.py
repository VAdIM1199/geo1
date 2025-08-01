import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """
Доступные команды:
/show_city [город] [цвет] - показать город на карте (цвет необязателен)
/remember_city [город] - сохранить город
/show_my_cities [цвет] - показать все сохраненные города (цвет необязателен)
/distance [город1] [город2] [цвет] - показать расстояние между городами (цвет необязателен)

Доступные цвета: red, blue, green, yellow, purple, orange, black
"""
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Использование: /show_city [город] [цвет]")
        return
    
    city_name = parts[1]
    color = parts[2] if len(parts) > 2 else 'red' 
    
    user_id = message.chat.id
    manager.create_graph(f'{user_id}.png', [city_name], color=color)
    with open(f'{user_id}.png', 'rb') as map_file:
        bot.send_photo(user_id, map_file)

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Использование: /remember_city [город]")
        return
    
    user_id = message.chat.id
    city_name = parts[1]
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    parts = message.text.split()
    color = parts[1] if len(parts) > 1 else 'blue'  
    
    cities = manager.select_cities(message.chat.id)
    if cities:
        manager.create_graph(f'{message.chat.id}_cities.png', cities, color=color)
        with open(f'{message.chat.id}_cities.png', 'rb') as map_file:
            bot.send_photo(message.chat.id, map_file)
    else:
        bot.send_message(message.chat.id, "У вас пока нет сохраненных городов.")

@bot.message_handler(commands=['distance'])
def handle_distance(message):
    parts = message.text.split()
    if len(parts) < 3:
        bot.send_message(message.chat.id, "Использование: /distance [город1] [город2] [цвет]")
        return
    
    city1 = parts[1]
    city2 = parts[2]
    color = parts[3] if len(parts) > 3 else 'green' 
    
    user_id = message.chat.id
    if manager.draw_distance(city1, city2, f'{user_id}_distance.png', color):
        with open(f'{user_id}_distance.png', 'rb') as map_file:
            bot.send_photo(user_id, map_file)
    else:
        bot.send_message(message.chat.id, "Один из городов не найден. Проверьте названия.")

if __name__=="__main__":
    manager = DB_Map(DATABASE)
    bot.polling()
