import telebot
import yt_dlp
import instaloader
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the bot with the token from .env
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# States to track the progress of the bot
user_states = {}

# Handle the /download command
@bot.message_handler(commands=['download'])
def send_welcome(message):
    bot.reply_to(message, "Send me a link to download.")
    user_states[message.chat.id] = 'awaiting_link'

# Handle text messages (user sending the link)
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_link')
def download_media(message):
    url = message.text
    bot.reply_to(message, "Wait, the media is downloading...")
    
    # Determine if it's a YouTube or Instagram link
    if 'youtube.com' in url or 'youtu.be' in url:
        file_path = download_youtube_shorts(url)
    elif 'instagram.com' in url:
        file_path = download_instagram_reel(url)
    else:
        bot.reply_to(message, "This link is not recognized.")
        return

    # If the file was successfully downloaded, send it
    if file_path:
        bot.reply_to(message, "The file is ready, sending now...")
        with open(file_path, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)
        os.remove(file_path)  # Clean up
    else:
        bot.reply_to(message, "Failed to download the media.")
    
    user_states[message.chat.id] = None

def download_youtube_shorts(url):
    """Download YouTube Shorts using yt-dlp."""
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Tries best video and audio, then best if combined
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,  # To avoid downloading a playlist if the link is part of one
            'merge_output_format': 'mp4',  # Ensure output format is mp4
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info_dict)
    except Exception as e:
        print(f"Error downloading YouTube video: {e}")
        return None

def download_instagram_reel(url):
    """Download Instagram Reels using instaloader."""
    try:
        loader = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(loader.context, url.split("/")[-2])
        loader.download_post(post, target="downloads")
        return f"downloads/{post.shortcode}.mp4"
    except Exception as e:
        print(f"Error downloading Instagram Reel: {e}")
        return None

# Start the bot
bot.polling()

