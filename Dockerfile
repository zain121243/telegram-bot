FROM python:3.11

# تثبيت ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# مجلد العمل
WORKDIR /app

# نسخ الملفات
COPY . .

# تثبيت المكتبات
RUN pip install -r requirements.txt

# تشغيل البوت
CMD ["python", "bot.py"]
