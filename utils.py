import yt_dlp as youtube_dl
import config
import telebot

def is_subscribed(bot, user_id):
    try:
        chat_member = bot.get_chat_member(config.CHANNEL_USERNAME, user_id)
        print(f"Chat member status: {chat_member.status}")  # Qo'shimcha yordamchi xabar
        return chat_member.status in ['member', 'administrator', 'creator']
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Error checking subscription status: {e}")
        return False

def download_video_from_url(url):
    try:
        ydl_opts = {
            'outtmpl': 'video.%(ext)s',
            'verbose': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info_dict)
        return video_file, None
    except Exception as e:
        return None, str(e)

# path/to/your/exported/cookies.txt
