from aria2p import API as Aria2API, Client as Aria2Client
import asyncio
from dotenv import load_dotenv
from datetime import datetime
import os
import logging
import math
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait
import time
import urllib.parse
from urllib.parse import urlparse
from flask import Flask, render_template
from threading import Thread

load_dotenv('config.env', override=True)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(name)s - %(levelname)s] %(message)s - %(filename)s:%(lineno)d"
)

logger = logging.getLogger(__name__)

logging.getLogger("pyrogram.session").setLevel(logging.ERROR)
logging.getLogger("pyrogram.connection").setLevel(logging.ERROR)
logging.getLogger("pyrogram.dispatcher").setLevel(logging.ERROR)

aria2 = Aria2API(
    Aria2Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)
options = {
    "max-tries": "50",
    "retry-wait": "3",
    "continue": "true",
    "allow-overwrite": "true",
    "min-split-size": "4M",
    "split": "10"
}

aria2.set_global_options(options)

# Environment variables validation
API_ID = os.environ.get('TELEGRAM_API', '')
API_HASH = os.environ.get('TELEGRAM_HASH', '')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
DUMP_CHAT_ID = os.environ.get('DUMP_CHAT_ID', '')
USER_SESSION_STRING = os.environ.get('USER_SESSION_STRING', '')

if not all([API_ID, API_HASH, BOT_TOKEN, DUMP_CHAT_ID]):
    logging.error("Missing required environment variables! Exiting now")
    exit(1)

DUMP_CHAT_ID = int(DUMP_CHAT_ID)

app = Client("jetbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user = None
SPLIT_SIZE = 2093796556  # 2GB for bot account
if USER_SESSION_STRING:
    user = Client("jetu", api_id=API_ID, api_hash=API_HASH, session_string=USER_SESSION_STRING)
    SPLIT_SIZE = 4241280205  # 4GB for user account

VALID_DOMAINS = [
    'terabox.com', 'nephobox.com', '4funbox.com', 'mirrobox.com',
    'momerybox.com', 'teraboxapp.com', '1024tera.com',
    'terabox.app', 'gibibox.com', 'goaibox.com', 'terasharelink.com',
    'teraboxlink.com', 'terafileshare.com', 'teraboxshare.com'
]

def is_valid_terabox_url(url):
    try:
        parsed = urlparse(url)
        if not parsed.scheme in ('http', 'https'):
            return False
        return any(parsed.netloc.endswith(domain) for domain in VALID_DOMAINS)
    except:
        return False

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("ᴊᴏɪɴ ❤️☠️", url="https://t.me/Drxupdates")],
        [InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ ⚡️", url="https://t.me/rtx5069")],
        [InlineKeyboardButton("ʀᴇᴘᴏ 🌐", url="https://github.com/Hrishi2861/Terabox-Downloader-Bot")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    welcome_msg = f"ᴡᴇʟᴄᴏᴍᴇ, {message.from_user.mention}.\n\n🌟 ɪ ᴀᴍ ᴀ ᴛᴇʀᴀʙᴏx ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ. sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴛᴇʀᴀʙᴏx ʟɪɴᴋ ɪ ᴡɪʟʟ ᴅᴏᴡɴʟᴏᴀᴅ ᴡɪᴛʜɪɴ ғᴇᴡ sᴇᴄᴏɴᴅs ᴀɴᴅ sᴇɴᴅ ɪᴛ ᴛᴏ ʏᴏᴜ ✨."
    
    video_path = "/app/Jet-Mirror.mp4"
    if os.path.exists(video_path):
        await client.send_video(
            chat_id=message.chat.id,
            video=video_path,
            caption=welcome_msg,
            reply_markup=reply_markup
        )
    else:
        await message.reply_text(welcome_msg, reply_markup=reply_markup)

async def update_status_message(message, text):
    try:
        await message.edit_text(text)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await update_status_message(message, text)
    except Exception as e:
        logger.error(f"Error updating status: {e}")

@app.on_message(filters.text & ~filters.command())
async def handle_terabox_link(client: Client, message: Message):
    # Extract URL from message
    urls = [word for word in message.text.split() if is_valid_terabox_url(word)]
    
    if not urls:
        # Only reply once if the message doesn't contain a valid URL
        if not message.text.startswith('/'):
            await message.reply_text("Please send me a valid Terabox download link.")
        return
    
    url = urls[0]  # Process only the first valid URL
    
    try:
        encoded_url = urllib.parse.quote(url)
        final_url = f"https://teradlrobot.cheemsbackup.workers.dev/?url={encoded_url}"
        
        download = aria2.add_uris([final_url])
        status_msg = await message.reply_text("Starting download... Please wait ⏳")
        
        start_time = datetime.now()
        last_update = time.time()
        UPDATE_INTERVAL = 15
        
        while not download.is_complete:
            await asyncio.sleep(10)
            download.update()
            
            if time.time() - last_update >= UPDATE_INTERVAL:
                elapsed = datetime.now() - start_time
                elapsed_str = f"{elapsed.seconds // 60}m {elapsed.seconds % 60}s"
                
                status_text = (
                    f"┏ ғɪʟᴇɴᴀᴍᴇ: {download.name}\n"
                    f"┠ [{''.join('★' for _ in range(int(download.progress/10)))}{''.join('☆' for _ in range(10-int(download.progress/10)))}] {download.progress:.2f}%\n"
                    f"┠ ᴘʀᴏɢʀᴇss: {format_size(download.completed_length)} / {format_size(download.total_length)}\n"
                    f"┠ sᴛᴀᴛᴜs: 📥 Downloading\n"
                    f"┠ sᴘᴇᴇᴅ: {format_size(download.download_speed)}/s\n"
                    f"┠ ᴇʟᴀᴘsᴇᴅ: {elapsed_str}\n"
                    f"┖ ᴜsᴇʀ: <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
                )
                
                await update_status_message(status_msg, status_text)
                last_update = time.time()
        
        # Download complete
        file_path = download.files[0].path
        file_size = os.path.getsize(file_path)
        
        caption = (
            f"✨ {download.name}\n"
            f"👤 ʟᴇᴇᴄʜᴇᴅ ʙʏ: <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>\n"
            f"📥 ᴜsᴇʀ ʟɪɴᴋ: tg://user?id={message.from_user.id}\n\n"
            "[ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴊᴇᴛ-ᴍɪʀʀᴏʀ ❤️☠️](https://t.me/Drxupdates)"
        )
        
        await update_status_message(status_msg, f"Download complete! Preparing to upload {download.name} ({format_size(file_size)})...")
        
        # Handle upload
        if file_size > SPLIT_SIZE:
            await handle_large_upload(client, message, file_path, caption, status_msg)
        else:
            await handle_normal_upload(client, message, file_path, caption, status_msg)
            
    except Exception as e:
        logger.error(f"Error processing Terabox link: {e}")
        await message.reply_text(f"Failed to process the Terabox link: {str(e)}")
    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            await status_msg.delete()
        except:
            pass

async def handle_normal_upload(client, message, file_path, caption, status_msg):
    try:
        if USER_SESSION_STRING:
            sent = await user.send_video(
                DUMP_CHAT_ID,
                file_path,
                caption=caption,
                progress=upload_progress,
                progress_args=(status_msg,)
            )
            await client.copy_message(message.chat.id, DUMP_CHAT_ID, sent.id)
        else:
            sent = await client.send_video(
                DUMP_CHAT_ID,
                file_path,
                caption=caption,
                progress=upload_progress,
                progress_args=(status_msg,)
            )
            await client.send_video(
                message.chat.id,
                sent.video.file_id,
                caption=caption
            )
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise

async def handle_large_upload(client, message, file_path, caption, status_msg):
    try:
        await update_status_message(status_msg, f"File too large ({format_size(os.path.getsize(file_path))}), splitting...")
        
        # Split the file
        split_files = await split_file(file_path, status_msg)
        
        for i, part in enumerate(split_files):
            part_caption = f"{caption}\n\nPart {i+1}/{len(split_files)}"
            await update_status_message(
                status_msg,
                f"Uploading part {i+1}/{len(split_files)}\n"
                f"{os.path.basename(part)}"
            )
            
            if USER_SESSION_STRING:
                sent = await user.send_video(
                    DUMP_CHAT_ID,
                    part,
                    caption=part_caption,
                    progress=upload_progress,
                    progress_args=(status_msg,)
                )
                await client.copy_message(message.chat.id, DUMP_CHAT_ID, sent.id)
            else:
                sent = await client.send_video(
                    DUMP_CHAT_ID,
                    part,
                    caption=part_caption,
                    progress=upload_progress,
                    progress_args=(status_msg,)
                )
                await client.send_video(
                    message.chat.id,
                    sent.video.file_id,
                    caption=part_caption
                )
            
            try:
                os.remove(part)
            except:
                pass
    except Exception as e:
        logger.error(f"Large upload error: {e}")
        raise

async def split_file(input_path, status_msg):
    try:
        base_name = os.path.splitext(input_path)[0]
        ext = os.path.splitext(input_path)[1] or '.mp4'
        
        # Get file duration using ffprobe
        proc = await asyncio.create_subprocess_exec(
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', input_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        duration = float(stdout.decode().strip())
        
        file_size = os.path.getsize(input_path)
        parts = math.ceil(file_size / SPLIT_SIZE)
        
        if parts == 1:
            return [input_path]
        
        part_duration = duration / parts
        output_files = []
        
        for i in range(parts):
            output_path = f"{base_name}.part{i+1:03d}{ext}"
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(i * part_duration),
                '-i', input_path,
                '-t', str(part_duration),
                '-c', 'copy',
                '-map', '0',
                '-avoid_negative_ts', 'make_zero',
                output_path
            ]
            
            proc = await asyncio.create_subprocess_exec(*cmd)
            await proc.wait()
            
            if os.path.exists(output_path):
                output_files.append(output_path)
            
            await update_status_message(
                status_msg,
                f"Splitting file...\n"
                f"Part {i+1}/{parts} completed"
            )
        
        return output_files
    except Exception as e:
        logger.error(f"Error splitting file: {e}")
        raise

async def upload_progress(current, total, status_msg):
    progress = (current / total) * 100
    try:
        await status_msg.edit_text(
            f"Uploading...\n"
            f"Progress: {progress:.2f}%\n"
            f"Uploaded: {format_size(current)} / {format_size(total)}"
        )
    except:
        pass

# Flask keep-alive
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Terabox Downloader Bot is running!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

def keep_alive():
    Thread(target=run_flask).start()

async def start_user_client():
    if user:
        await user.start()
        logger.info("User client started")

if __name__ == "__main__":
    keep_alive()
    
    if USER_SESSION_STRING:
        logger.info("Starting user client...")
        Thread(target=lambda: asyncio.run(start_user_client())).start()
    
    logger.info("Starting bot client...")
    app.run()
