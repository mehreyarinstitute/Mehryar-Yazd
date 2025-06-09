import os
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import threading

# توکن ربات از متغیر محیطی
TOKEN = os.environ["TOKEN"]

# ایجاد سرور Flask برای جلوگیری از خوابیدن سرویس
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/ping')
def ping():
    return "pong"

# فرمان /start برای ارسال دکمه‌ها
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

# پاسخ به کلیک روی دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = {
        'python': "🔧 آموزش پایتون",
        'ai': "🤖 هوش مصنوعی جذابه!",
        'language': "🗣 یادگیری زبان خیلی مهمه",
        'resin': "🎨 رزین یک هنر زیباست",
        'crypto': "💰 دنیای ارز دیجیتال پرهیجانه!",
        'painting': "🖌 نقاشی یعنی خلاقیت",
        'computer': "🖥 دنیای کامپیوتر بی‌پایانه"
    }
    await query.edit_message_text(data.get(query.data, "گزینه‌ای ناشناس انتخاب شد."))

# راه‌اندازی ربات
def run_bot():
    app_telegram = ApplicationBuilder().token(TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(button_handler))
    print("🤖 ربات در حال اجراست...")
    app_telegram.run_polling()

# اجرای همزمان Flask و ربات
if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8000)).start()
    run_bot()
