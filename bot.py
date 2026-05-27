import os
import asyncio
import re
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, DOWNLOAD_PATH

bot = Client("VideoDownloaderBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Supported platforms regex
URL_PATTERN = re.compile(r'(https?://[^\s]+)')

async def download_video(url: str, message: Message):
    status_msg = await message.reply_text("⬇️ **Downloading...**")

    ydl_opts = {
        'format': 'best[height<=720]',  # Good quality, smaller size
        'outtmpl': f'{DOWNLOAD_PATH}/%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Video')

        await status_msg.edit_text("📤 **Uploading...**")

        await message.reply_video(
            video=open(filename, "rb"),
            caption=f"✅ **Downloaded Successfully**\n**Title:** {title}\n**Source:** {url[:50]}...",
            supports_streaming=True
        )

        await status_msg.delete()
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await status_msg.edit_text(f"❌ **Failed to download**\nError: {str(e)[:800]}")

@bot.on_message(filters.regex(URL_PATTERN) & (filters.private | filters.group))
async def link_handler(_, message: Message):
    urls = URL_PATTERN.findall(message.text)
    
    for url in urls:
        # Filter supported platforms
        if any(platform in url.lower() for platform in ['instagram.com', 'youtube.com', 'youtu.be', 'pinterest.com', 'pin.it']):
            await download_video(url, message)

@bot.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text(
        "🎥 **Multi Platform Video Downloader**\n\n"
        "Just send any **Instagram Reel**, **YouTube Video**, or **Pinterest Video** link.\n"
        "I will download and send it automatically!"
    )

async def main():
    await bot.start()
    print("🚀 Video Downloader Bot Started Successfully!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
