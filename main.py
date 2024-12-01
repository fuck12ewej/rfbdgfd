import random
import string
import telebot
import json
import os
from telebot import types

API_TOKEN = "7735484805:AAEUOQkhFN0aSCPUGXXNbEObVRwqorca434"  # Замените на ваш реальный токен
bot = telebot.TeleBot(API_TOKEN)

# Путь к файлу конфигурации
CONFIG_FILE = "config.json"

# Загружаем или создаем конфигурацию
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
    return {"user_profiles": {}}

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print("Конфигурация успешно сохранена.")
    except Exception as e:
        print(f"Ошибка при сохранении конфигурации: {e}")

# Загрузка конфигурации
config = load_config()
user_profiles = config.get("user_profiles", {})

# Генерация данных пользователя
def generate_promo_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def generate_secret_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# Создание или получение профиля пользователя
def get_or_create_user_profile(user_id):
    user_id_str = str(user_id)
    if user_id_str not in user_profiles:
        user_profiles[user_id_str] = {
            "secret_id": generate_secret_id(),
            "balance": 0,
            "total_profit": 0,
            "transactions": 0,
            "refunds": 0,
            "monthly_profit": 0,
            "last_profit_date": "0",
            "promo_code": generate_promo_code()
        }
        save_config({"user_profiles": user_profiles})  # Сохранение новой конфигурации
    return user_profiles[user_id_str]

# Клавиатуры
def main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("👤 Профиль", "🏅 Топ воркеров", "📌 Навигация", "🔗 Ссылки")
    return markup

def navigation_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📕 Мануал сленга скамера", "📕 Обязательный мануал для новичков", "Назад")
    return markup

# Обработчики
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    get_or_create_user_profile(user_id)
    bot.send_message(user_id, "Добро пожаловать! Выберите действие:", reply_markup=main_menu_keyboard())

@bot.message_handler(func=lambda message: message.text == "👤 Профиль")
def profile(message):
    user_id = message.from_user.id
    profile = get_or_create_user_profile(user_id)
    bot.send_message(
        user_id,
        f"👤 Ваш профиль:\n"
        f"☠️ SecretID: {profile['secret_id']}\n"
        f"💰 Баланс: {profile['balance']} руб.\n"
        f"💰 Общий доход: {profile['total_profit']} руб.\n"
        f"💎 Промокод: {profile['promo_code']}\n"
        f"📅 Последний профит: {profile['last_profit_date']}",
        reply_markup=main_menu_keyboard()  # Добавим клавиатуру после вывода профиля
    )

@bot.message_handler(func=lambda message: message.text == "🏅 Топ воркеров")
def top_workers(message):
    if not user_profiles:
        bot.send_message(message.chat.id, "Топ пользователей пока недоступен.", reply_markup=main_menu_keyboard())
        return
    
    top_profiles = sorted(user_profiles.items(), key=lambda x: x[1]['total_profit'], reverse=True)
    top_3 = top_profiles[:3]
    top_message = "🏅 Топ воркеров:\n"
    
    for i, (user_id, profile) in enumerate(top_3, 1):
        username = bot.get_chat(user_id).username if bot.get_chat(user_id).username else "Без_ника"
        top_message += f"\n#{i} - @{username} - {profile['total_profit']} руб."
    
    bot.send_message(message.chat.id, top_message, reply_markup=main_menu_keyboard())

@bot.message_handler(func=lambda message: message.text == "📌 Навигация")
def navigation(message):
    bot.send_message(
        message.chat.id,
        "📌 Навигация по функциям:",
        reply_markup=navigation_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "📕 Мануал сленга скамера")
def send_scam_slanga_manual(message):
    try:
        with open('slang_manual.txt', 'rb') as manual_file:
            bot.send_document(message.chat.id, manual_file)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Извините, файл slang_manual.txt не найден. Пожалуйста, обратитесь к администратору.")

@bot.message_handler(func=lambda message: message.text == "📕 Обязательный мануал для новичков")
def send_manual(message):
    try:
        with open('manual.txt', 'rb') as manual_file:
            bot.send_document(message.chat.id, manual_file)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Извините, файл gg.txt не найден. Пожалуйста, обратитесь к администратору.")

@bot.message_handler(func=lambda message: message.text == "🔗 Ссылки")
def links(message):
    bot.send_message(
        message.chat.id,
        "🔗 Ссылки:\n"
        "👩‍💻 Сайт для ворка - http://kinoroom.great-site.net"
        "                             💎Генератор ссылки - your_link_generator_url_here",
        reply_markup=main_menu_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "Назад")
def back_to_main_menu(message):
    bot.send_message(
        message.chat.id,
        "Вы вернулись в главное меню.",
        reply_markup=main_menu_keyboard()
    )

# Пример команды для обновления профиля
@bot.message_handler(func=lambda message: message.text.startswith("Обновить прибыль"))
def update_profit(message):
    try:
        profit_amount = int(message.text.split()[2])  # предполагаем, что текст будет в формате "Обновить прибыль 5000"
        user_id = message.from_user.id
        profile = get_or_create_user_profile(user_id)
        profile['total_profit'] += profit_amount  # Обновляем общий доход
        save_config({"user_profiles": user_profiles})  # Сохраняем обновленные данные
        bot.send_message(
            message.chat.id,
            f"Ваш общий доход обновлен на {profit_amount} руб.",
            reply_markup=main_menu_keyboard()
        )
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка. Пожалуйста, используйте формат 'Обновить прибыль <сумма>'.")

if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}")
