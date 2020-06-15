import telebot
import config
import dbworker
import functions

from pyowm.commons.exceptions import PyOWMError
from telebot import types


bot = telebot.TeleBot(config.token)
notes = {}

keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('Okey..', '/reset')

keyboard2 = telebot.types.ReplyKeyboardMarkup()
keyboard2.row('/weather', '/news', '/remind')

keyboard3 = telebot.types.ReplyKeyboardMarkup()
keyboard3.row('/weather', '/menu')

keyboard4 = telebot.types.ReplyKeyboardMarkup()
keyboard4.row('/rewrite', '/menu')

keyboard5 = telebot.types.ReplyKeyboardMarkup()
keyboard5.row('/news', '/menu')


@bot.message_handler(commands=['start'], content_types=['text'])
def start_message(message):
    bot.send_message(message.chat.id, 'Running depression systems')
    state = dbworker.get_current_state(message.chat.id)
    if state == config.States.S_ENTER_NAME.value:
        bot.send_message(message.chat.id, "I need to know your name, you did not write it..")
    elif state == config.States.S_ENTER_AGE.value:
        bot.send_message(message.chat.id, config.name + ", it seems that someone promised to send his age, but never did...")
    elif state == config.States.S_END.value:
        bot.send_message(message.chat.id, "Continue our conversation?", reply_markup=keyboard1)
    else:  # Под "остальным" понимаем состояние "0" - начало диалога
        bot.send_message(message.chat.id, "Hi... What is your name?")
        dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)


# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Well, let's start in a new way.. What's your name?")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)


@bot.message_handler(commands=['menu'])
def weather_menu(message):
    bot.send_message(message.chat.id, config.name + ". What would you like?", reply_markup=keyboard2)


@bot.message_handler(commands=['weather'])
def command_weather(message):
    sent = bot.send_message(message.chat.id, "Write the name of the city", reply_markup=keyboard3)
    bot.register_next_step_handler(sent, send_forecast)


def send_forecast(message):
    try:
        functions.day_weather(message.text)
    except PyOWMError:
        bot.send_message(message.chat.id, "I don't know this city")
        return
    today_weather = functions.day_weather(message.text)
    bot.send_message(message.chat.id,
                     f"Weather in City {message.text} for today:\nMin temperature: {today_weather[0]}"
                     f"\nMax temperature: {today_weather[1]}"
                     f"\nCurrent temperature: {today_weather[2]}"
                     f"\n{today_weather[3]}")


@bot.message_handler(commands=['news'])
def command_news(message):
    bot.send_message(message.chat.id, "Last news:\n", reply_markup=keyboard5)
    bot.send_message(message.chat.id, functions.get_article(), parse_mode='HTML')
    markup = types.InlineKeyboardMarkup()
    btn_my_site = types.InlineKeyboardButton(text='Source', url='https://www.bbc.com/news/')
    markup.add(btn_my_site)
    bot.send_message(message.chat.id, "Here is the news source.", reply_markup=markup,)


@bot.message_handler(commands=['remind'])
def remind(message):
    user_id = message.chat.id
    if user_id not in notes:
        note = bot.send_message(user_id, "You haven’t written to me yet..\nWhat should I remember?", reply_markup=keyboard4)
        bot.register_next_step_handler(note, remember)
    else:
        bot.send_message(user_id, notes[user_id], reply_markup=keyboard4)


def remember(message):
    user_id = message.chat.id
    notes[user_id] = message.text
    bot.send_message(user_id, "I'll remember")


@bot.message_handler(commands=['rewrite'])
def remind(message):
    user_id = message.chat.id
    note = bot.send_message(user_id, "What should I remember?")
    bot.register_next_step_handler(note, remember2)


def remember2(message):
    user_id = message.chat.id
    notes[user_id] = message.text
    bot.send_message(user_id, "I'll remember")


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NAME.value)
def user_entering_name(message):
    config.name = message.text
    bot.send_message(message.chat.id, "Great name, I'll try to remember... Now please tell me your age.")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_AGE.value)


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_AGE.value)
def user_entering_age(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Something is wrong, try again...")
        return
    else:
        bot.send_message(message.chat.id, "Once upon a time I was your age... But let's not get distracted.")
        config.age = message.text
        dbworker.set_state(message.chat.id, config.States.S_END.value)
        bot.send_sticker(message.chat.id, config.stickerid)
        bot.send_message(message.chat.id, "Greetings, " + config.name + " I'm Marvin, the Paranoid Android...\nI think you ought to know I'm feeling very depressed".format(message.from_user, bot.get_me()), reply_markup=keyboard1,
                         parse_mode='html')


@bot.message_handler(content_types=['text'])
def main_menu_message(message):
    if message.text.lower() == 'okey..':
        bot.send_message(message.chat.id, config.name + ", i'll be your personal assistant...\nWhat would you like?".format(message.from_user, bot.get_me()), reply_markup=keyboard2,
                         parse_mode='html')


bot.polling(none_stop=True)
