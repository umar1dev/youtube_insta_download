import yt_dlp as youtube_dl
import config
import telebot
from telebot import types
import logging

def is_subscribed(bot, user_id):
    try:
        chat_member = bot.get_chat_member(config.CHANNEL_USERNAME, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Error checking subscription status: {e}")
def download_video_from_url(url):
    try:
        ydl_opts = {
            'outtmpl': 'downloads/video.%(ext)s',  # Video faylni 'downloads' papkada saqlash
            'verbose': True,
            'username': 'your_instagram_username',  # Instagram login
            'password': 'your_instagram_password',  # Instagram password
            'cookies': 'path/to/cookies.txt',  # Cookies fayl yo'li
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info_dict)
        return video_file, None
    except Exception as e:
        logging.error(f"Video yuklab olishda xatolik: {str(e)}")
        return None, "Video yuklab olishda xatolik yuz berdi."



def send_welcome(bot, message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Kanalga obuna bo'lish", url=f"https://t.me/{config.CHANNEL_USERNAME[1:]}")
    markup.add(btn)
    bot.send_message(message.chat.id, "Botdan foydalanish uchun kanalimizga obuna bo'ling.", reply_markup=markup)

def confirm_subscription(bot, message):
    user_id = message.from_user.id
    if is_subscribed(bot, user_id):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        confirm_button = types.KeyboardButton('Tasdiqlash')
        markup.add(confirm_button)
        bot.send_message(message.chat.id, "Kanalga obuna bo'lganingiz tasdiqlandi. Tasdiqlash tugmasini bosing va keyin video linkini yuboring.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Kanalga obuna bo'lmagansiz. Iltimos, obuna bo'ling.")

def handle_text_message(bot, message):
    user_id = message.from_user.id
    if is_subscribed(bot, user_id):
        if message.text.lower() == 'tasdiqlash':
            bot.send_message(message.chat.id, "Endi video linkini yuboring.")
        else:
            url = message.text
            video_file, error = download_video_from_url(url)
            if video_file:
                bot.send_video(message.chat.id, open(video_file, 'rb'))
            else:
                bot.send_message(message.chat.id, "Video yuklab olishda xatolik yuz berdi.")
                if error:
                    bot.send_message(config.ADMIN_USER_ID, f"Video yuklab olishda xatolik: {str(error)}")
    else:
        bot.send_message(message.chat.id, "Iltimos, avval kanalga obuna bo'ling va tasdiqlang.")
