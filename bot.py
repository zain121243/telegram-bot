import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🎬 فيديو
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.video.get_file()
        await file.download_to_drive("input.mp4")

        cmd = 'ffmpeg -i input.mp4 -i logo.png -filter_complex "[1:v]scale=200:-1,format=rgba,colorchannelmixer=aa=0.5[logo];[0:v][logo]overlay=(W-w)/2:(H-h)/2" -y output.mp4'

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            await update.message.reply_text(result.stderr)
            return

        await update.message.reply_video(video=open("output.mp4", "rb"))

    except Exception as e:
        await update.message.reply_text(str(e))


# 🖼 صورة (نسخة مستقرة جدًا)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive("input.jpg")

        cmd = 'ffmpeg -i input.jpg -i logo.png -filter_complex "[1:v]scale=200:-1,format=rgba,colorchannelmixer=aa=0.5[logo];[0:v][logo]overlay=(W-w)/2:(H-h)/2" -y output.jpg'

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            await update.message.reply_text(result.stderr)
            return

        await update.message.reply_photo(photo=open("output.jpg", "rb"))

    except Exception as e:
        await update.message.reply_text(str(e))


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Bot is running...")

app.run_polling()
