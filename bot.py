import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🎬 معالجة الفيديو (شعار متحرك)
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.video.get_file()
        await file.download_to_drive("input.mp4")

        cmd = 'ffmpeg -i input.mp4 -i logo.png -filter_complex "[1:v]scale=200:-1,format=rgba,colorchannelmixer=aa=0.5[logo];[0:v][logo]overlay=(W-w)/2+20*sin(t*2):(H-h)/2+20*cos(t*2)" -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p -c:a copy -y output.mp4'

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            await update.message.reply_text("خطأ:\n" + result.stderr)
            return

        if not os.path.exists("output.mp4"):
            await update.message.reply_text("ما تم إنشاء الفيديو ❌")
            return

        await update.message.reply_video(video=open("output.mp4", "rb"))

    except Exception as e:
        await update.message.reply_text(str(e))


# 🖼 معالجة الصور (شعار ثابت بالمنتصف)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive("input.jpg")

        cmd = 'ffmpeg -i input.jpg -i logo.png -filter_complex "[1:v]scale=200:-1,format=rgba,colorchannelmixer=aa=0.5[logo];[0:v][logo]overlay=(W-w)/2:(H-h)/2" -y output.jpg'

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            await update.message.reply_text("خطأ:\n" + result.stderr)
            return

        if not os.path.exists("output.jpg"):
            await update.message.reply_text("ما تم إنشاء الصورة ❌")
            return

        await update.message.reply_photo(photo=open("output.jpg", "rb"))

    except Exception as e:
        await update.message.reply_text(str(e))


# تشغيل البوت
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Bot is running...")

app.run_polling()
