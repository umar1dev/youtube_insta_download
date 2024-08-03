import os
import logging
import telebot
from telebot import types
import yt_dlp

# Telegram botining konfiguratsiyasi
API_TOKEN = '7283654983:AAGgLtjl4f0PrPVmuxpxrhP0K27ufUtbJ_0'
CHANNEL_USERNAME_1 = '@kinolar_770'
CHANNEL_USERNAME_2 = '@videolar_55'
ADMIN_USER_ID = 6663856218

bot = telebot.TeleBot(API_TOKEN)

# Obuna bo'lishni tekshiruvchi funksiya
def is_subscribed(bot, user_id, channel_username):
    try:
        chat_member = bot.get_chat_member(channel_username, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except telebot.apihelper.ApiTelegramException as e:
        if e.error_code == 400:
            bot.send_message(user_id, "Kanalga obuna bo'lishni tekshirishda xatolik yuz berdi. Iltimos, botni kanalga admin qilib qo'shing.")
        else:
            bot.send_message(user_id, f"Xatolik: {e.description}")
        return False

# Ikkala kanalga obuna bo'lganligini tekshiruvchi funksiya
def is_subscribed_to_both(bot, user_id):
    return is_subscribed(bot, user_id, CHANNEL_USERNAME_1) and is_subscribed(bot, user_id, CHANNEL_USERNAME_2)

# Videoni yuklab olish funksiyasi
def download_video_from_url(url):
    try:
        ydl_opts = {
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'cookiefile': 'C:/Users/Acer/Desktop/cookies.txt',
            'verbose': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.18 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate'
            }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(result)
            return video_file, None
    except Exception as e:
        logging.error(f"Video yuklab olishda xatolik: {str(e)}")
        return None, "Video yuklab olishda xatolik yuz berdi."

# Boshlang'ich xabarni yuboruvchi funksiya
def send_welcome(bot, message):
    markup = types.InlineKeyboardMarkup()
    btn_subscribe_1 = types.InlineKeyboardButton("Kanalga obuna bo'lish👀", url=f"https://t.me/{CHANNEL_USERNAME_1[1:]}")
    btn_subscribe_2 = types.InlineKeyboardButton("Kanalga obuna bo'lish👀", url=f"https://t.me/{CHANNEL_USERNAME_2[1:]}")
    btn_confirm = types.InlineKeyboardButton("Tasdiqlash✅", callback_data='confirm')
    markup.row(btn_subscribe_1)
    markup.row(btn_subscribe_2)
    markup.add(btn_confirm)
    bot.send_message(message.chat.id, "Botdan foydalanish uchun kanallarga obuna bo'ling va Tasdiqlang✅", reply_markup=markup)

# Obuna bo'lishni tasdiqlovchi funksiya
def confirm_subscription(bot, message):
    user_id = message.from_user.id
    if is_subscribed_to_both(bot, user_id):
        bot.send_message(message.chat.id, "Kanallarga obuna bo'lganingiz Tasdiqlandi✅. Endi video linkini yuboring.")
    else:
        bot.send_message(message.chat.id, "Kanallarga obuna bo'lmagansiz. Iltimos, Kanallarga obuna bo'ling!")

# Matnli xabarni qayta ishlovchi funksiya
def handle_text_message(bot, message):
    user_id = message.from_user.id
    if is_subscribed_to_both(bot, user_id):
        url = message.text
        if url.startswith('http://') or url.startswith('https://'):
            loading_message = bot.send_message(message.chat.id, "⌛")
            video_file, error = download_video_from_url(url)
            bot.delete_message(message.chat.id, loading_message.message_id)
            if video_file:
                bot.send_video(message.chat.id, open(video_file, 'rb'))
            else:
                bot.send_message(message.chat.id, "Video yuklab olishda xatolik yuz berdi.")
                if error:
                    bot.send_message(ADMIN_USER_ID, f"Video yuklab olishda xatolik: {str(error)}")
        else:
            bot.send_message(message.chat.id, "Iltimos, to'g'ri URL yuboring!")
    else:
        bot.send_message(message.chat.id, "Iltimos, avval kanallarga obuna bo'ling va tasdiqlang.")

# Botni ishga tushirish
@bot.message_handler(commands=['start'])
def handle_start(message):
    send_welcome(bot, message)

@bot.message_handler(content_types=['text'])
def handle_message(message):
    handle_text_message(bot, message)

@bot.callback_query_handler(func=lambda call: call.data == 'confirm')
def handle_confirm_button(call):
    confirm_subscription(bot, call.message)

bot.polling()
