import os
import asyncio
import re
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, DOWNLOAD_PATH

bot = Client("CosmicSaverBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

URL_PATTERN = re.compile(r'https?://[^\s]+')

async def download_media(url: str, message: Message):
    status = await message.reply_text("⬇️ **Downloading...**")
    ydl_opts = {
        'format': 'best[height<=720]/best',
        'outtmpl': f'{DOWNLOAD_PATH}/%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Media')

        await status.edit_text("📤 **Uploading...**")
        await message.reply_video(open(filename, "rb"), caption=f"✅ Saved: {title}", supports_streaming=True)
        await status.delete()

        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)[:400]}")

@bot.on_message(filters.text & (filters.private | filters.group) & \~filters.command(["start"]))
async def link_handler(_, message: Message):
    urls = URL_PATTERN.findall(message.text or "")
    for url in urls:
        if any(x in url.lower() for x in ['instagram', 'youtube', 'youtu.be', 'tiktok', 'pinterest']):
            await download_media(url, message)

@bot.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text("🎥 **Cosmic Saver Bot**\n\nJust send any video link!")

async def main():
    await bot.start()
    print("🚀 Bot Started!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
