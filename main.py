import telebot
import logging
import re
import csv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from decouple import config
from fall import show_poem, read_meanings_from_xlsx, get_random_meaning
from image import make_image
from flask import Flask, request
import json
import requests

# logging info
logging.basicConfig(filename='info.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(filename)s - %(message)s')

DEBUG = config('DEBUG', default=True, cast=bool)

TOKEN = config('TOKEN')
bot = telebot.TeleBot(token=TOKEN, threaded=False)

DISCORD_WEBHOOK_URL = config('DISCORD_WEBHOOK_URL')

# تابع برای ذخیره شناسه کاربر
def save_user_id(user_id):
    try:
        with open('users.json', 'r') as file:
            users = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        users = []

    if user_id not in users:
        users.append(user_id)

    with open('users.json', 'w') as file:
        json.dump(users, file)

def send_log_to_discord(log_message):
    data = {
        "content": log_message
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code != 204:
        logging.error(f"Failed to send log to Discord: {response.status_code}, {response.text}")

if not DEBUG:
    secret = config('SECRET')
    url = f'{config("URL")}/{secret}'

    bot.remove_webhook()
    bot.set_webhook(url=url)

    app = Flask(__name__)

    message_bool = False

    @app.route(f'/{secret}', methods=['POST'])
    def webhook():
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return 'ok', 200

files = dict()

with open('list.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            pass
        files[row["file"]] = row["id"]

# مسیر فایل اکسل
xlsx_path = 'Faal.xlsx'

# خواندن تفسیرها از ستون سوم فایل اکسل
meanings = read_meanings_from_xlsx(xlsx_path)

@bot.message_handler(commands=['start', 'help'])
def start(msg):
    user_id = msg.chat.id
    save_user_id(user_id)
    logging.info(f'{msg.chat.username} - {msg.chat.id}')
    send_log_to_discord(f'New user: {msg.chat.username} - {msg.chat.id}')

    text = """
سلام
با یار یلدا می‌توانید در بلندترین شب سال، از اشعار دلنشین حافظ لذت ببرید و آینده خود را در آینه حکمت و معرفت او ببینید. یار یلدا، همدم شما در شب یلدا و راهنمایی روشن در تاریکی این شب طولانی است.

اگر هم میخواهید که فال بگیرید میتونید روی دکمه ی «فالم رو بگیر!» لمس کنید یا دستور /fall رو ارسال کنید.
"""

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("فالم رو بگیر!", callback_data="get_fall"),
        InlineKeyboardButton("🔗 ارتباط با تیم سازنده", url="https://ContactWithMamrez.t.me"),
    )
    photo_path = 'Faal-post.png'
    with open(photo_path, 'rb') as photo:
        bot.send_photo(msg.chat.id, photo, caption=text, reply_markup=markup)

    # bot.reply_to(msg, text, reply_markup=markup)

def fall(chat_id, username):
    random_meaning = get_random_meaning(meanings)
    text_of_divination = show_poem(random_meaning)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        # InlineKeyboardButton("🔗 ارتباط با تیم سازنده", url="https://ContactWithMamrez.t.me"),
    )

    bot.send_message(chat_id, text_of_divination, parse_mode="markdown", reply_markup=markup)

    # ارسال لاگ فال گرفته شده به وبهوک دیسکورد
    log_message = f"User: {username} - {chat_id}\nCommand: /fall\nDivination: {text_of_divination}"
    send_log_to_discord(log_message)

@bot.message_handler(commands=['fall'])
def get_fall(msg):
    fall(msg.chat.id, msg.chat.username)

def get_fallow_markup(poem=None):
    markup = InlineKeyboardMarkup(row_width=1)

    # if poem == None:
    #     # markup.add(InlineKeyboardButton("🔗 ارتباط با تیم سازنده", url="https://ContactWithMamrez.t.me"))
    # else:
    #     markup.add(
    #         # InlineKeyboardButton("تصویر بده!", callback_data=f"get_pic-{poem}"),
    #         # InlineKeyboardButton("🔗 ارتباط با تیم سازنده", url="https://ContactWithMamrez.t.me"),
    #     )

    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "get_fall":
        fall(call.message.chat.id, call.from_user.username)
    elif str(call.data).split('-')[0] == "get_pic":
        file_name = str(call.data).split('-')[1]
        poem = make_image(file_name)
        pic = open(poem, 'rb')
        text = '@YarYalda_Bot'
        bot.send_photo(call.message.chat.id, pic, caption=text, reply_markup=get_fallow_markup())
    elif str(call.data).split('-')[0] == "get_audio":
        file_name = str(call.data).split('-')[1]
        bot.copy_message(call.message.chat.id, config('STORAGE'), int(files[file_name]), reply_markup=get_fallow_markup())

@bot.message_handler(content_types=['text'])
def get_poem(msg):
    poem = re.findall(r"\d+", str(msg.text))
    if poem != []:
        poem = int(poem[0])
        if poem in range(1, 496):
            text_of_poem = show_poem(f"sh{poem}")
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                # InlineKeyboardButton("تصویر بده!", callback_data=f"get_pic-sh{poem}"),
                # InlineKeyboardButton("خوانش این غزل...", callback_data=f"get_audio-sh{poem}"),
                # InlineKeyboardButton("🔗 ارتباط با تیم سازنده", url="https://ContactWithMamrez.t.me"),
            )
            bot.send_message(msg.chat.id, text_of_poem, reply_markup=markup)

            # ارسال لاگ استفاده از دستور /fall
            log_message = f"User: {msg.chat.username} - {msg.chat.id}\nCommand: /fall\nDivination: {text_of_poem}"
            send_log_to_discord(log_message)
        else:
            bot.send_message(msg.chat.id, 'فال امسالت رو مهمون ما باش')
    else:
        bot.send_message(msg.chat.id, 'فال امسالت رو مهمون ما باش')

        # ارسال لاگ استفاده از دستور /fall
        log_message = f"User: {msg.chat.username} - {msg.chat.id}\nCommand: /fall\nDivination: Invalid poem number"
        send_log_to_discord(log_message)

if DEBUG:
    bot.infinity_polling()