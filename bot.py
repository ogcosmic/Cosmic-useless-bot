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
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Media')

        await status.edit_text("📤 **Uploading...**")

        if filename.endswith(('.mp4', '.mov', '.webm')):
            await message.reply_video(
                open(filename, "rb"),
                caption=f"✅ **Saved by Cosmic Saver Bot**\n**Title:** {title[:100]}",
                supports_streaming=True
            )
        else:
            await message.reply_document(open(filename, "rb"), caption=f"✅ Saved: {title}")

        await status.delete()

        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await status.edit_text(f"❌ Failed: {str(e)[:500]}\n\nTry a public link.")

@bot.on_message((filters.private | filters.group) & \~filters.command(["start"]))
async def link_handler(_, message: Message):
    if not message.text:
        return

    urls = URL_PATTERN.findall(message.text)
    for url in urls:
        lower_url = url.lower()
        if any(domain in lower_url for domain in [
            'instagram.com', 'youtu.be', 'youtube.com',
            'tiktok.com', 'pinterest.com', 'pin.it'
        ]):
            await download_media(url, message)

@bot.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply_text(
        "🎥 **Cosmic Saver Bot** (@CosmicSaverBot)\n\n"
        "Just send any link from:\n"
        "• Instagram Reels / Posts\n"
        "• YouTube Videos / Shorts\n"
        "• TikTok\n"
        "• Pinterest\n\n"
        "No commands needed! Just paste the link."
    )

async def main():
    await bot.start()
    print("🚀 Cosmic Saver Bot (like TopSaverBot) is Running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
