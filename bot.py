from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from logic import *
import schedule
import threading
import time
from config import *

bot = TeleBot(API_TOKEN)

# Для хранения, кто уже получил приз (user_id: set(prize_id))
winners_cache = {}

def gen_markup(prize_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Получить!", callback_data=str(prize_id)))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        prize_id = int(call.data)
        user_id = call.message.chat.id

        # Проверяем, не получил ли уже этот пользователь этот приз
        if winners_cache.get(prize_id, set()).__contains__(user_id):
            bot.answer_callback_query(call.id, "Ты уже получил этот приз!")
            return

        # Проверяем, не превышен ли лимит (3 пользователя)
        if len(winners_cache.get(prize_id, set())) >= 3:
            bot.answer_callback_query(call.id, "Приз уже разобрали!")
            return

        # Добавляем победителя в базу и кэш
        if manager.add_winner(user_id, prize_id):
            winners_cache.setdefault(prize_id, set()).add(user_id)
            img = manager.get_prize_img(prize_id)
            with open(f'img/{img}', 'rb') as photo:
                bot.send_photo(user_id, photo, caption="Поздравляем! Ты получил приз!")
            bot.answer_callback_query(call.id, "Поздравляем! Ты получил приз!")
        else:
            bot.answer_callback_query(call.id, "Ты уже участвовал за этот приз!")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка: {e}")

def send_message():
    prize = manager.get_random_prize()
    if not prize:
        print("Нет доступных призов!")
        return
    prize_id, img = prize[:2]
    manager.mark_prize_used(prize_id)
    hide_img(img)
    winners_cache[prize_id] = set()  # Сбросить кэш для нового приза
    for user in manager.get_users():
        try:
            with open(f'hidden_img/{img}', 'rb') as photo:
                bot.send_photo(user, photo, reply_markup=gen_markup(prize_id))
        except Exception as e:
            print(f"Ошибка отправки пользователю {user}: {e}")

def shedule_thread():
    schedule.every(100).seconds.do(send_message)  # Периодичность отправки
    while True:
        schedule.run_pending()
        time.sleep(1)

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    users = manager.get_users()
    if user_id in users:
        bot.reply_to(message, "Ты уже зарегистрирован!")
    else:
        manager.add_user(user_id, message.from_user.username or "")
        bot.reply_to(message, """Привет! Добро пожаловать! 
Тебя успешно зарегистрировали!
Каждый час тебе будут приходить новые картинки и у тебя будет шанс их получить!
Для этого нужно быстрее всех нажать на кнопку 'Получить!'

Только три первых пользователя получат картинку!)""")

def polling_thread():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    manager = DatabaseManager(DATABASE)
    manager.create_tables()

    polling_thread_obj = threading.Thread(target=polling_thread)
    polling_shedule_obj = threading.Thread(target=shedule_thread)

    polling_thread_obj.start()
    polling_shedule_obj.start()