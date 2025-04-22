from aria2p import API as Aria2API, Client as Aria2Client
import asyncio
from dotenv import load_dotenv
from datetime import datetime
import os
import logging
import math
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
import time
import urllib.parse
from urllib.parse import urlparse
from flask import Flask, render_template
from threading import Thread
import re

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

API_ID = os.environ.get('TELEGRAM_API', '')
if len(API_ID) == 0:
    logging.error("TELEGRAM_API variable is missing! Exiting now")
    exit(1)

API_HASH = os.environ.get('TELEGRAM_HASH', '')
if len(API_HASH) == 0:
    logging.error("TELEGRAM_HASH variable is missing! Exiting now")
    exit(1)
    
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    logging.error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

DUMP_CHAT_ID = os.environ.get('DUMP_CHAT_ID', '')
if len(DUMP_CHAT_ID) == 0:
    logging.error("DUMP_CHAT_ID variable is missing! Exiting now")
    exit(1)
else:
    DUMP_CHAT_ID = int(DUMP_CHAT_ID)

USER_SESSION_STRING = os.environ.get('USER_SESSION_STRING', '')
if len(USER_SESSION_STRING) == 0:
    logging.info("USER_SESSION_STRING variable is missing! Bot will split Files in 2Gb...")
    USER_SESSION_STRING = None

app = Client("jetbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user = None
SPLIT_SIZE = 2093796556
if USER_SESSION_STRING:
    user = Client("jetu", api_id=API_ID, api_hash=API_HASH, session_string=USER_SESSION_STRING)
    SPLIT_SIZE = 4241280205

VALID_DOMAINS = [
    'terabox.com', 'nephobox.com', '4funbox.com', 'mirrobox.com', 
    'momerybox.com', 'teraboxapp.com', '1024tera.com', 
    'terabox.app', 'gibibox.com', 'goaibox.com', 'terasharelink.com', 
    'teraboxlink.com', 'terafileshare.com', 'teraboxshare.com'
]
last_update_time = 0

def is_valid_url(url):
    parsed_url = urlparse(url)
    return any(parsed_url.netloc.endswith(domain) for domain in VALID_DOMAINS)

def extract_links(text):
    # Extract URLs from text
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    links = re.findall(url_pattern, text)
    
    # Filter for valid Terabox domains
    terabox_links = [link for link in links if is_valid_url(link)]
    return terabox_links

def format_size(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️☠️", url="https://t.me/Drxupdates")
    developer_button = InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ ⚡️", url="https://t.me/rtx5069")
    repo69 = InlineKeyboardButton("ʀᴇᴘᴏ 🌐", url="https://github.com/Hrishi2861/Terabox-Downloader-Bot")
    user_mention = message.from_user.mention
    reply_markup = InlineKeyboardMarkup([[join_button, developer_button], [repo69]])
    final_msg = f"ᴡᴇʟᴄᴏᴍᴇ, {user_mention}.\n\n🌟 ɪ ᴀᴍ ᴀ ᴛᴇʀᴀʙᴏx ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ. sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴛᴇʀᴀʙᴏx ʟɪɴᴋ ɪ ᴡɪʟʟ ᴅᴏᴡɴʟᴏᴀᴅ ᴡɪᴛʜɪɴ ғᴇᴡ sᴇᴄᴏɴᴅs ᴀɴᴅ sᴇɴᴅ ɪᴛ ᴛᴏ ʏᴏᴜ ✨.\n\n✅ ʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ sᴇɴᴅ ᴍᴜʟᴛɪᴘʟᴇ ᴛᴇʀᴀʙᴏx ʟɪɴᴋs ɪɴ ᴏɴᴇ ᴍᴇssᴀɢᴇ!"
    video_file_id = "/app/Jet-Mirror.mp4"
    if os.path.exists(video_file_id):
        await client.send_video(
            chat_id=message.chat.id,
            video=video_file_id,
            caption=final_msg,
            reply_markup=reply_markup
            )
    else:
        await message.reply_text(final_msg, reply_markup=reply_markup)

async def update_status_message(status_message, text):
    try:
        await status_message.edit_text(text)
    except Exception as e:
        logger.error(f"Failed to update status message: {e}")

async def download_and_upload(client, message, url, user_id, index=None, total=None):
    encoded_url = urllib.parse.quote(url)
    final_url = f"https://teradlrobot.cheemsbackup.workers.dev/?url={encoded_url}"

    suffix = ""
    if index and total:
        suffix = f" (ʟɪɴᴋ {index}/{total})"
        
    status_message = await message.reply_text(f"sᴇɴᴅɪɴɢ ʏᴏᴜ ᴛʜᴇ ᴍᴇᴅɪᴀ...😴{suffix}")
    
    download = aria2.add_uris([final_url])
    start_time = datetime.now()

    while not download.is_complete:
        await asyncio.sleep(15)
        try:
            download.update()
            progress = download.progress

            elapsed_time = datetime.now() - start_time
            elapsed_minutes, elapsed_seconds = divmod(elapsed_time.seconds, 60)

            status_text = (
                f"┏ ғɪʟᴇɴᴀᴍᴇ: {download.name}{suffix}\n"
                f"┠ [{'★' * int(progress / 10)}{'☆' * (10 - int(progress / 10))}] {progress:.2f}%\n"
                f"┠ ᴘʀᴏᴄᴇssᴇᴅ: {format_size(download.completed_length)} ᴏғ {format_size(download.total_length)}\n"
                f"┠ sᴛᴀᴛᴜs: 📥 Downloading\n"
                f"┠ ᴇɴɢɪɴᴇ: <b><u>Aria2c v1.37.0</u></b>\n"
                f"┠ sᴘᴇᴇᴅ: {format_size(download.download_speed)}/s\n"
                f"┠ ᴇᴛᴀ: {download.eta} | ᴇʟᴀᴘsᴇᴅ: {elapsed_minutes}m {elapsed_seconds}s\n"
                f"┖ ᴜsᴇʀ: <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> | ɪᴅ: {user_id}\n"
            )
            while True:
                try:
                    await update_status_message(status_message, status_text)
                    break
                except FloodWait as e:
                    logger.error(f"Flood wait detected! Sleeping for {e.value} seconds")
                    await asyncio.sleep(e.value)
        except Exception as e:
            logger.error(f"Error updating download status: {e}")
            await asyncio.sleep(5)

    try:
        file_path = download.files[0].path
        caption = (
            f"✨ {download.name}\n"
            f"👤 ʟᴇᴇᴄʜᴇᴅ ʙʏ : <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>\n"
            f"📥 ᴜsᴇʀ ʟɪɴᴋ: tg://user?id={user_id}\n\n"
            f"[ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴊᴇᴛ-ᴍɪʀʀᴏʀ ❤️☠️](https://t.me/Drxupdates)"
        )

        if index and total:
            caption += f"\n\nʟɪɴᴋ {index} ᴏғ {total}"

        last_update_time = time.time()
        UPDATE_INTERVAL = 15

        async def update_status(message, text):
            nonlocal last_update_time
            current_time = time.time()
            if current_time - last_update_time >= UPDATE_INTERVAL:
                try:
                    await message.edit_text(text)
                    last_update_time = current_time
                except FloodWait as e:
                    logger.warning(f"FloodWait: Sleeping for {e.value}s")
                    await asyncio.sleep(e.value)
                    await update_status(message, text)
                except Exception as e:
                    logger.error(f"Error updating status: {e}")

        async def upload_progress(current, total):
            progress = (current / total) * 100
            elapsed_time = datetime.now() - start_time
            elapsed_minutes, elapsed_seconds = divmod(elapsed_time.seconds, 60)

            status_text = (
                f"┏ ғɪʟᴇɴᴀᴍᴇ: {download.name}{suffix}\n"
                f"┠ [{'★' * int(progress / 10)}{'☆' * (10 - int(progress / 10))}] {progress:.2f}%\n"
                f"┠ ᴘʀᴏᴄᴇssᴇᴅ: {format_size(current)} ᴏғ {format_size(total)}\n"
                f"┠ sᴛᴀᴛᴜs: 📤 Uploading to Telegram\n"
                f"┠ ᴇɴɢɪɴᴇ: <b><u>PyroFork v2.2.11</u></b>\n"
                f"┠ sᴘᴇᴇᴅ: {format_size(current / elapsed_time.seconds if elapsed_time.seconds > 0 else 0)}/s\n"
                f"┠ ᴇʟᴀᴘsᴇᴅ: {elapsed_minutes}m {elapsed_seconds}s\n"
                f"┖ ᴜsᴇʀ: <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> | ɪᴅ: {user_id}\n"
            )
            await update_status(status_message, status_text)

        async def split_video_with_ffmpeg(input_path, output_prefix, split_size):
            try:
                original_ext = os.path.splitext(input_path)[1].lower() or '.mp4'
                start_time = datetime.now()
                last_progress_update = time.time()
                
                proc = await asyncio.create_subprocess_exec(
                    'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1', input_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc.communicate()
                total_duration = float(stdout.decode().strip())
                
                file_size = os.path.getsize(input_path)
                parts = math.ceil(file_size / split_size)
                
                if parts == 1:
                    return [input_path]
                
                duration_per_part = total_duration / parts
                split_files = []
                
                for i in range(parts):
                    current_time = time.time()
                    if current_time - last_progress_update >= UPDATE_INTERVAL:
                        elapsed = datetime.now() - start_time
                        status_text = (
                            f"✂️ Splitting {os.path.basename(input_path)}{suffix}\n"
                            f"Part {i+1}/{parts}\n"
                            f"Elapsed: {elapsed.seconds // 60}m {elapsed.seconds % 60}s"
                        )
                        await update_status(status_message, status_text)
                        last_progress_update = current_time
                    
                    output_path = f"{output_prefix}.{i+1:03d}{original_ext}"
                    cmd = [
                        'xtra', '-y', '-ss', str(i * duration_per_part),
                        '-i', input_path, '-t', str(duration_per_part),
                        '-c', 'copy', '-map', '0',
                        '-avoid_negative_ts', 'make_zero',
                        output_path
                    ]
                    
                    proc = await asyncio.create_subprocess_exec(*cmd)
                    await proc.wait()
                    split_files.append(output_path)
                
                return split_files
            except Exception as e:
                logger.error(f"Split error: {e}")
                raise

        async def handle_upload():
            file_size = os.path.getsize(file_path)
            
            if file_size > SPLIT_SIZE:
                await update_status(
                    status_message,
                    f"✂️ Splitting {download.name} ({format_size(file_size)}){suffix}"
                )
                
                split_files = await split_video_with_ffmpeg(
                    file_path,
                    os.path.splitext(file_path)[0],
                    SPLIT_SIZE
                )
                
                try:
                    for i, part in enumerate(split_files):
                        part_caption = f"{caption}\n\nPart {i+1}/{len(split_files)}"
                        await update_status(
                            status_message,
                            f"📤 Uploading part {i+1}/{len(split_files)}{suffix}\n"
                            f"{os.path.basename(part)}"
                        )
                        
                        if USER_SESSION_STRING:
                            sent = await user.send_video(
                                DUMP_CHAT_ID, part, 
                                caption=part_caption,
                                progress=upload_progress
                            )
                            await app.copy_message(
                                message.chat.id, DUMP_CHAT_ID, sent.id
                            )
                        else:
                            sent = await client.send_video(
                                DUMP_CHAT_ID, part,
                                caption=part_caption,
                                progress=upload_progress
                            )
                            await client.send_video(
                                message.chat.id, sent.video.file_id,
                                caption=part_caption
                            )
                        os.remove(part)
                finally:
                    for part in split_files:
                        try: os.remove(part)
                        except: pass
            else:
                await update_status(
                    status_message,
                    f"📤 Uploading {download.name}{suffix}\n"
                    f"Size: {format_size(file_size)}"
                )
                
                if USER_SESSION_STRING:
                    sent = await user.send_video(
                        DUMP_CHAT_ID, file_path,
                        caption=caption,
                        progress=upload_progress
                    )
                    await app.copy_message(
                        message.chat.id, DUMP_CHAT_ID, sent.id
                    )
                else:
                    sent = await client.send_video(
                        DUMP_CHAT_ID, file_path,
                        caption=caption,
                        progress=upload_progress
                    )
                    await client.send_video(
                        message.chat.id, sent.video.file_id,
                        caption=caption
                    )
            if os.path.exists(file_path):
                os.remove(file_path)

        start_time = datetime.now()
        await handle_upload()

        try:
            await status_message.delete()
        except Exception as e:
            logger.error(f"Status message delete error: {e}")
            
        return True
    except Exception as e:
        logger.error(f"Error during file processing: {e}")
        await status_message.edit_text(f"❌ Error processing file: {str(e)[:200]}")
        return False

@app.on_message(filters.text)
async def handle_message(client: Client, message: Message):
    if message.text.startswith('/'):
        return
    if not message.from_user:
        return

    user_id = message.from_user.id
    
    # Extract all Terabox links from the message
    links = extract_links(message.text)
    
    if not links:
        await message.reply_text("Please provide at least one valid Terabox link.")
        return
    
    # If more than one link found, notify the user
    if len(links) > 1:
        await message.reply_text(f"✅ Found {len(links)} Terabox links. Processing them one by one...")
    
    # Process each link sequentially
    original_message = message
    for i, link in enumerate(links, 1):
        try:
            success = await download_and_upload(client, original_message, link, user_id, i, len(links))
            if not success:
                await message.reply_text(f"❌ Failed to process link {i}/{len(links)}: {link}")
            
            # Add a small delay between processing multiple links
            if i < len(links):
                await asyncio.sleep(3)
        except Exception as e:
            logger.error(f"Error processing link {i}/{len(links)}: {e}")
            await message.reply_text(f"❌ Error processing link {i}/{len(links)}")
    
    try:
        # Delete original message after all links are processed
        await original_message.delete()
    except Exception as e:
        logger.error(f"Original message delete error: {e}")

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return render_template("index.html")

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

def keep_alive():
    Thread(target=run_flask).start()

async def start_user_client():
    if user:
        await user.start()
        logger.info("User client started.")

def run_user():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_user_client())

if __name__ == "__main__":
    keep_alive()

    if user:
        logger.info("Starting user client...")
        Thread(target=run_user).start()

    logger.info("Starting bot client...")
    app.run()
