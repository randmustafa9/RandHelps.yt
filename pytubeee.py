import os, re, datetime, unicodedata
from pytube import YouTube
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import re
import moviepy.editor as mp
from telegram.ext import CommandHandler, MessageHandler, filters, Application, CallbackQueryHandler



# Telegram Bot Token and Username
bot_token = ''
bot_username = "@"



# Handler for the /start command
async def start(update: Update, context):
    await update.message.reply_text("Welcome to RandHelps.yt Bot. Downloading YouTube videos and audio is a breeze—just share a valid YouTube link. Should you have any questions or need assistance, please don't hesitate to reach out.")



# Handler for processing user-provided YouTube links
async def get_yt_url(update: Update, context):
    # Regular expression pattern to match YouTube URLs
    youtube_url_pattern = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$"
    user_message = update.message.text
    context.user_data['user_message'] = user_message
    
    # Notify admin about the received message
    await context.bot.send_message(chat_id=0, text=f"(@{update.message.from_user.username}) got :  {user_message}")

    if re.match(youtube_url_pattern, user_message): 
        # Create an inline keyboard for user options
        keyboard = [
            [
                InlineKeyboardButton("Get video", callback_data="1"),
            ],
            [
                InlineKeyboardButton("Get audio", callback_data="2"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Prompt the user to choose an option
        await update.message.reply_text("Please choose:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Please enter a valid YouTube link.")




# Handler for processing user choice (video or audio)
async def download_yt_vid(update: Update, context):
    query = update.callback_query
    option = query.data
    current_datetime = datetime.datetime.now()
    timestamp = int(current_datetime.timestamp())
    user_message = context.user_data.get('user_message')
    yt = YouTube(user_message)
    desktop_path = ""
    
    # Notify the user that the download is in progress
    await query.message.reply_text(f"Downloading from {user_message}")

    # Send the downloaded file
    chat_id = query.message.chat_id
    stream = yt.streams.get_highest_resolution()
    stream.download(output_path=desktop_path)

    audio_file_path = os.path.join(desktop_path, stream.default_filename)
    mp4_file_path = os.path.join(desktop_path, convert_to_ascii(stream.default_filename))

    # Attempt to change the modification date
    try:
        os.utime(mp4_file_path, (timestamp, timestamp))
        print(f"Modified file '{mp4_file_path}' date to {current_datetime}.")
    except Exception as e:
        print(f"Failed to modify file date: {e}")

    new_mp4_file, file_extension = os.path.splitext(os.path.basename(mp4_file_path))
    mp3_output_path = os.path.join(desktop_path, new_mp4_file + ".mp3")  # MP3 format

    if option == "1":
        # Send the video file
        document = open(audio_file_path, 'rb')
        await query.message.reply_text(f"Uploading video...")
        await context.bot.send_document(chat_id, document)
        document.close()
    elif option == "2":
        # Rename the file to its original name
        os.rename(audio_file_path, mp4_file_path)
        
        # Load the downloaded audio
        clip = mp.VideoFileClip(mp4_file_path)

        # Convert to MP3 format
        clip.audio.write_audiofile(mp3_output_path)
        clip.audio.reader.close_proc()
        document2 = open(mp3_output_path, 'rb')
        
        # Send the audio file
        await query.message.reply_text(f"Uploading audio...")
        await context.bot.send_document(chat_id, document2)
        document2.close()
        clip.reader.close()
        clip.close()

    # Cleanup downloaded files
    await delete_file(desktop_path)




# Function to convert non-ASCII characters in a filename
def convert_to_ascii(filename):
    filename = filename.replace(' ', '_').replace('.', '_').replace('-', '_')
    filename = ''.join(c for c in unicodedata.normalize('NFD', filename) if unicodedata.category(c) != 'Mn')
    filename = filename.encode('ascii', 'ignore').decode('ascii')[0:-3]
    return filename




# Function to delete files in a directory
async def delete_file(ppath):
    files = os.listdir(ppath)
    for filename in files:
        filepath = os.path.join(ppath, filename)
        try:
            os.remove(filepath)
            print(f"Deleted: {filepath}")
        except Exception as e:
            print(f"Failed to delete: {filepath} - {e}")
    print(f"All files in {ppath} have been deleted.")




# Handler to send a message to the admin
async def send_message(update, context):
    await context.bot.send_message(chat_id=0, text=f"Message from (@{update.message.from_user.username}) :   Thank you Rand for YouTube Bot!")

    await update.message.reply_text("Your message has been sent to Rand!")


        




if __name__ == '__main__':


    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("Thanks", send_message))
    app.add_handler(MessageHandler(filters.TEXT, get_yt_url))

    app.add_handler(CallbackQueryHandler(download_yt_vid))

   # app.add_error_handler(error)
    print('pooling...')
    app.run_polling(poll_interval=3)








