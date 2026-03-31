import os
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

user_settings = {}

# 🎬 استقبال الفيديو
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.video.get_file()
    await file.download_to_drive("input.mp4")

    user_settings[update.effective_user.id] = {"type": "video"}

    keyboard = [
        [InlineKeyboardButton("⬆️ أعلى", callback_data="top"),
         InlineKeyboardButton("⬇️ أسفل", callback_data="bottom")],
        [InlineKeyboardButton("⬅️ يسار", callback_data="left"),
         InlineKeyboardButton("➡️ يمين", callback_data="right")],
        [InlineKeyboardButton("🎯 وسط", callback_data="center")]
    ]

    await update.message.reply_text("اختر مكان اللوكو:", reply_markup=InlineKeyboardMarkup(keyboard))


# 🖼 استقبال الصورة
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file()
    await file.download_to_drive("input.jpg")

    user_settings[update.effective_user.id] = {"type": "photo"}

    keyboard = [
        [InlineKeyboardButton("⬆️ أعلى", callback_data="top"),
         InlineKeyboardButton("⬇️ أسفل", callback_data="bottom")],
        [InlineKeyboardButton("⬅️ يسار", callback_data="left"),
         InlineKeyboardButton("➡️ يمين", callback_data="right")],
        [InlineKeyboardButton("🎯 وسط", callback_data="center")]
    ]

    await update.message.reply_text("اختر مكان اللوكو:", reply_markup=InlineKeyboardMarkup(keyboard))


# 📍 اختيار المكان
async def choose_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_settings[query.from_user.id]["position"] = query.data

    keyboard = [
        [InlineKeyboardButton("🔹 صغير", callback_data="small"),
         InlineKeyboardButton("🔸 متوسط", callback_data="medium"),
         InlineKeyboardButton("🔶 كبير", callback_data="large")]
    ]

    await query.edit_message_text("اختر حجم اللوكو:", reply_markup=InlineKeyboardMarkup(keyboard))


# 📏 اختيار الحجم + التنفيذ
async def choose_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = user_settings.get(query.from_user.id)
    position = data["position"]
    size = query.data

    # 📏 تحديد الحجم
    if size == "small":
        scale = 100
    elif size == "medium":
        scale = 150
    else:
        scale = 220

    # 📍 تحديد المكان
    positions = {
        "top": "(W-w)/2:20",
        "bottom": "(W-w)/2:H-h-20",
        "left": "20:(H-h)/2",
        "right": "W-w-20:(H-h)/2",
        "center": "(W-w)/2:(H-h)/2"
    }

    overlay = positions.get(position)

    await query.edit_message_text("⏳ جاري المعالجة...")

    try:
        if data["type"] == "video":
            cmd = f'ffmpeg -i input.mp4 -i logo.png -filter_complex "[1:v]scale={scale}:-1[logo];[0:v][logo]overlay={overlay}" -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p -c:a copy -y output.mp4'
            output_file = "output.mp4"
        else:
            cmd = f'ffmpeg -i input.jpg -i logo.png -filter_complex "[1:v]scale={scale}:-1[logo];[0:v][logo]overlay={overlay}" -y output.jpg'
            output_file = "output.jpg"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            await query.message.reply_text(result.stderr)
            return

        if data["type"] == "video":
            await context.bot.send_video(query.from_user.id, video=open(output_file, "rb"))
        else:
            await context.bot.send_photo(query.from_user.id, photo=open(output_file, "rb"))

        os.remove(output_file)

    except Exception as e:
        await query.message.reply_text(str(e))


# 🚀 تشغيل
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(CallbackQueryHandler(choose_position, pattern="^(top|bottom|left|right|center)$"))
app.add_handler(CallbackQueryHandler(choose_size, pattern="^(small|medium|large)$"))

print("Bot is running...")

app.run_polling()
