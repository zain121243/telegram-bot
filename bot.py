import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# جلب التوكن من Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")

# معالجة الفيديو
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.video.get_file()
        await file.download_to_drive("input.mp4")

        result = subprocess.run(
            'ffmpeg -i input.mp4 -i logo.png -filter_complex "overlay=10:10" -y output.mp4',
            shell=True,
            capture_output=True,
            text=True
        )

        # إذا ffmpeg فشل
        if result.returncode != 0:
            await update.message.reply_text("خطأ ffmpeg:\n" + result.stderr)
            return

        if not os.path.exists("output.mp4"):
            await update.message.reply_text("ما تم إنشاء الفيديو ❌")
            return

        await update.message.reply_video(video=open("output.mp4", "rb"))

    except Exception as e:
        await update.message.reply_text(f"خطأ:\n{e}")

# معالجة الصور
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive("input.jpg")

        result = subprocess.run(
            'ffmpeg -i input.jpg -i logo.png -filter_complex "overlay=10:10" -y output.jpg',
            shell=True,
            capture_output=True,
            text=True
        )

        # إذا ffmpeg فشل
        if result.returncode != 0:
            await update.message.reply_text("خطأ ffmpeg:\n" + result.stderr)
            return

        if not os.path.exists("output.jpg"):
            await update.message.reply_text("ما تم إنشاء الصورة ❌")
            return

        await update.message.reply_photo(photo=open("output.jpg", "rb"))

    except Exception as e:
        await update.message.reply_text(f"خطأ:\n{e}")

# تشغيل البوت
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Bot is running...")

app.run_polling()
