import asyncio
import logging
import subprocess
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.types import Message, FSInputFile
from PIL import Image

BOT_TOKEN = "8596035534:AAEI7R7FDzpufLm0xJaXxZ0XfSAM3HRYzt8"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


def find_logo():
    for name in ("logo.png", "logo.jpg", "logo.jpeg", "logo.webp"):
        if Path(name).exists():
            return name
    return None


def run_ffmpeg(input_file: str, logo_file: str, output_file: str):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-i", logo_file,
        "-filter_complex",
        (
            "[1:v]scale=220:-1,format=rgba,colorchannelmixer=aa=0.28[logo];"
            "[0:v][logo]overlay=(W-w)/2:(H-h)/2"
        ),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "28",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        output_file,
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "FFmpeg failed")


@dp.message()
async def handle_all(message: Message):
    try:
        logo_file = find_logo()
        if not logo_file:
            await message.reply(
                "❌ لم أجد الشعار.\n"
                "ضعه داخل نفس المجلد باسم:\n"
                "logo.png"
            )
            return

        file_id = None
        input_file = None
        output_file = None
        is_video = False
        is_photo = False

        if message.video:
            file_id = message.video.file_id
            input_file = "input_video.mp4"
            output_file = "output_video.mp4"
            is_video = True

        elif message.photo:
            file_id = message.photo[-1].file_id
            input_file = "input_photo.jpg"
            output_file = "output_photo.jpg"
            is_photo = True

        elif message.document:
            mime = (message.document.mime_type or "").lower()

            if mime.startswith("video/"):
                file_id = message.document.file_id
                input_file = "input_video.mp4"
                output_file = "output_video.mp4"
                is_video = True

            elif mime.startswith("image/"):
                file_id = message.document.file_id
                input_file = "input_photo.jpg"
                output_file = "output_photo.jpg"
                is_photo = True

        if not file_id:
            await message.reply("📩 أرسل صورة أو فيديو فقط")
            return

        await message.reply("⏳ جارِ المعالجة...")

        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, input_file)

        if is_video:
            await asyncio.to_thread(run_ffmpeg, input_file, logo_file, output_file)
            await message.reply_video(FSInputFile(output_file))

        elif is_photo:
            img = Image.open(input_file).convert("RGBA")
            logo = Image.open(logo_file).convert("RGBA")

            target_width = max(120, img.width // 4)
            ratio = target_width / logo.width
            target_height = int(logo.height * ratio)
            logo = logo.resize((target_width, target_height))

            alpha = logo.getchannel("A")
            alpha = alpha.point(lambda p: int(p * 0.28))
            logo.putalpha(alpha)

            x = (img.width - logo.width) // 2
            y = (img.height - logo.height) // 2

            img.paste(logo, (x, y), logo)
            img = img.convert("RGB")
            img.save(output_file, quality=95)

            await message.reply_photo(FSInputFile(output_file))

    except Exception as e:
        print("ERROR:", repr(e))
        await message.reply(f"❌ خطأ:\n{repr(e)}")


async def main():
    while True:
        try:
            print("🚀 البوت يعمل...")
            await dp.start_polling(bot)
        except Exception as e:
            print("⚠️ انقطع الاتصال:", repr(e))
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())