import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("8596035534:AAEI7R7FDzpufLm0xJaXxZ0XfSAM3HRYzt8")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.video.get_file()
    await file.download_to_drive("input.mp4")

    os.system('ffmpeg -i input.mp4 -vf "drawtext=text=MyBot:fontcolor=white:fontsize=24:x=10:y=H-th-10" output.mp4')

    await update.message.reply_video(video=open("output.mp4", "rb"))

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.VIDEO, handle_video))

app.run_polling()
