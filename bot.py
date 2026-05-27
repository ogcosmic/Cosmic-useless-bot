import os
import asyncio
import re
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, DOWNLOAD_PATH

bot = Client("CosmicDownloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Improved URL Pattern
URL_PATTERN = re.compile(r'https?://[^\s]+')

async def download_video(url: str, message: Message):
    status = await message.reply_text("⬇️ **Downloading Reel/Video...**")

    ydl_opts = {
        'format': 'best[height<=720]',
        'outtmpl': f'{DOWNLOAD_PATH}/%(id)s.%(ext)s',
        'quiet': False,           # Changed to see errors
        'noplaylist': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Instagram Reel')

        await status.edit_text("📤 **Uploading to Telegram...**")

        await message.reply_video(
            video=open(filename, "rb"),
            caption=f"✅ **Downloaded by Cosmic Downloader**\n**Title:** {title}",
            supports_streaming=True
        )

        await status.delete()

        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await status.edit_text(f"❌ **Failed**\n{str(e)[:500]}")

@bot.on_message(filters.regex(URL_PATTERN) & (filters.private | filters.group))
async def link_handler(_, message: Message):
    urls = URL_PATTERN.findall(message.text)
    print(f"🔍 Detected {len(urls)} link(s): {urls}")  # For debugging

    for url in urls:
        if any(x in url.lower() for x in ['instagram.com/reel', 'instagram.com', 'youtube.com', 'youtu.be', 'pinterest.com']):
            await download_video(url, message)

@bot.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text(
        "🎥 **Cosmic Video Downloader**\n\n"
        "Just send any **Instagram Reel**, **YouTube**, or **Pinterest** link.\n"
        "I will download it automatically!"
    )

async def main():
    await bot.start()
    print("🚀 Cosmic Downloader Bot is Running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
