import telebot
import schedule
import time
from threading import Thread
from config.config import TOKEN
from telebot import types
from my_module.get_shop_info import start_update
from my_module.get_date import transform_date
from my_module.method_db import add_user, created_db, add_mailing, delete_mailing, get_mailing_user_all, get_profile

bot = telebot.TeleBot(TOKEN)
created_db()

def schedule_checker() -> None:
    while True:
        schedule.run_pending()
        time.sleep(1)

def function_to_run() -> None:
    start_update()
    id_list = get_mailing_user_all()
    weekday, day, month, year = transform_date()
    for id_el in id_list:
        bot.send_message(id_el[0], f"🛒Магазин предметов обновлён!\n📅{weekday}, {day} {month} {year}")
        file = open(f'../data/img/collage.jpg', 'rb')
        bot.send_photo(id_el[0], file)
    return


@bot.message_handler(commands=['start'])
def main(message):
    add_user(message) # Добавляем пользователя в БД

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton('Получать рассылку')
    btn2 = types.KeyboardButton('Не получать рассылку')
    markup.row(btn1, btn2)
    text = "Привет, я бот с рассылкой магазина в Fortnite.\nКогда магазин обновляется я сразу об этом узнаю и могу информировать тебя!)\nХочешь получать рассылку?"
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    add_mailing(message.from_user.id)
    bot.send_message(message.chat.id, '✅ SUCCESS ✅\nТы подписался на получение рассылки об обновлении магазина!\nЧтобы отписаться /unsubscribe')


@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    delete_mailing(message.from_user.id)
    bot.send_message(message.chat.id,'✅ SUCCESS ✅\nТы отписался от получения рассылки об обновлении магазина!\nЧтобы подписаться обратно /subscribe')


@bot.message_handler(commands=['shop_today'])
def shop_today(message):
    _, day, month, year = transform_date()
    bot.send_message(message.chat.id, f'🛒Магазин предметов на {day} {month} {year}')
    file = open(f'../data/img/collage.jpg', 'rb')
    bot.send_photo(message.chat.id, file)


@bot.message_handler(commands=['profile'])
def profile(message):
    user = get_profile(message.from_user.id)
    if user[0][3] == 0:
        bot.send_message(message.chat.id, f"💼Твой профиль💼\n\nИмя: 👔{message.from_user.username}\nСтатус подписки: ❌Отписан")
    else:
        bot.send_message(message.chat.id,
                         f"💼Твой профиль💼\n\nИмя: 👔{message.from_user.username}\nСтатус подписки: ✅Подписан")


@bot.message_handler()
def message_person(message):
    if message.text == "Не получать рассылку":
        delete_mailing(message.from_user.id)
        bot.send_message(message.chat.id, '✅ SUCCESS ✅\nХорошо, если захочешь - то команда /subscribe')
    elif message.text == "Получать рассылку":
        subscribe(message)


# Запускаем планировщик в отдельном потоке
schedule_thread = Thread(target=schedule_checker)
schedule_thread.daemon = True  # Устанавливаем демонский поток, чтобы он не блокировал завершение программы
schedule_thread.start()

if __name__ == "__main__":
    time_for_send = "00:19"
    schedule.every().day.at(time_for_send).do(function_to_run)

    # Начинаем обработку запросов
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

