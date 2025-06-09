import os
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import threading

# دریافت توکن از متغیر محیطی
TOKEN = os.environ["TOKEN"]

# راه‌اندازی Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/ping')
def ping():
    return "pong"

# دکمه‌های شیشه‌ای
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("پایتون", callback_data='python'),
         InlineKeyboardButton("هوش مصنوعی", callback_data='ai')],
        [InlineKeyboardButton("زبان", callback_data='language'),
         InlineKeyboardButton("رزین", callback_data='resin')],
        [InlineKeyboardButton("ارز دیجیتال", callback_data='crypto'),
         InlineKeyboardButton("نقاشی", callback_data='painting')],
        [InlineKeyboardButton("کامپیوتر", callback_data='computer')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! یکی از گزینه‌ها را انتخاب کن:", reply_markup=reply_markup)

# هندل کردن کلیک روی دکمه‌ها و ارسال عکس مربوطه
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # نگاشت نام دکمه به نام فایل عکس
    image_map = {
        'python': 'python.jpg',
        'ai': 'ai.jpg',
        'language': 'language.jpg',
        'resin': 'resin.jpg',
        'crypto': 'crypto.jpg',
        'painting': 'painting.jpg',
        'computer': 'computer.jpg',
    }

    image_file = image_map.get(query.data)

    if image_file and os.path.exists(image_file):
        with open(image_file, 'rb') as photo:
            await context.bot.send_photo(chat_id=query.message.chat.id, photo=photo)
    else:
        await query.edit_message_text("تصویر مربوطه پیدا نشد یا هنوز بارگذاری نشده است.")

# اجرای ربات
def run_bot():
    app_telegram = ApplicationBuilder().token(TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(button_handler))
    print("ربات در حال اجراست...")
    app_telegram.run_polling()

# اجرای همزمان ربات و Flask
if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8000)).start()
    run_bot()
