import telebot
from config import *
from logic import *
from datetime import datetime
import time

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    start_text = """
Привет! Я бот для работы с городами на карте.

Основные команды:
/country_cities [страна] - города страны
/density_cities [мин_плотность] - города с плотностью выше указанной
/city_info [город] - информация о городе
/time_info [город] - местное время города
/help - все команды
"""
    bot.send_message(message.chat.id, start_text)

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """
/country_cities [страна] - города страны
/density_cities [плотность] - города с плотностью выше
/city_info [город] - подробная информация
/time_info [город] - местное время

/show_city [город] - показать город
/remember_city [город] - сохранить город
/show_my_cities - показать сохраненные города
"""
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['country_cities'])
def handle_country_cities(message):
    try:
        country = message.text.split()[1]
        cities = manager.get_country_cities(country)
        
        if cities:
            manager.create_graph(f'{message.chat.id}_country.png', cities)
            with open(f'{message.chat.id}_country.png', 'rb') as f:
                bot.send_photo(message.chat.id, f)
            bot.send_message(message.chat.id, f"Города страны {country}: {', '.join(cities)}")
        else:
            bot.send_message(message.chat.id, "Города не найдены")
    except IndexError:
        bot.send_message(message.chat.id, "Укажите страну: /country_cities [страна]")

@bot.message_handler(commands=['density_cities'])
def handle_density_cities(message):
    try:
        min_density = float(message.text.split()[1])
        cities = manager.get_cities_by_density(min_density)
        
        if cities:
            manager.create_graph(f'{message.chat.id}_density.png', cities)
            with open(f'{message.chat.id}_density.png', 'rb') as f:
                bot.send_photo(message.chat.id, f)
            bot.send_message(message.chat.id, f"Города с плотностью > {min_density}: {', '.join(cities[:10])}" + 
                           ("..." if len(cities) > 10 else ""))
        else:
            bot.send_message(message.chat.id, "Города не найдены")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Укажите минимальную плотность: /density_cities [число]")

@bot.message_handler(commands=['city_info'])
def handle_city_info(message):
    try:
        city = message.text.split()[1]
        info = manager.get_city_info(city)
        
        if info:
            response = (f"Город: {city}\n"
                      f"Страна: {info['country']}\n"
                      f"Население: {info['population']:,}\n"
                      f"Плотность: {info['density']} чел/км²\n"
                      f"Часовой пояс: UTC{info['timezone']}")
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "Город не найден")
    except IndexError:
        bot.send_message(message.chat.id, "Укажите город: /city_info [город]")

@bot.message_handler(commands=['time_info'])
def handle_time_info(message):
    try:
        city = message.text.split()[1]
        timezone = manager.get_city_timezone(city)
        
        if timezone:
            utc_offset = float(timezone)
            local_time = datetime.utcnow().timestamp() + utc_offset * 3600
            time_str = time.strftime("%H:%M:%S", time.gmtime(local_time))
            bot.send_message(message.chat.id, f"В {city} сейчас: {time_str} (UTC{timezone})")
        else:
            bot.send_message(message.chat.id, "Город не найден")
    except IndexError:
        bot.send_message(message.chat.id, "Укажите город: /time_info [город]")


if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    bot.polling()
