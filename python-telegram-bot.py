import os
import threading
from flask import Flask
from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

TOKEN = os.environ["TOKEN"]
GROUP_CHAT_ID = -100xxxxxxxxxx  # <-- حتماً این عدد را با آیدی عددی گروه جایگزین کن!
app = Flask(__name__)

@app.route('/ping')
def ping():
    return 'pong'

# تعریف دکمه‌های دپارتمان
DEPARTMENTS = {
    "art": ("🎨 هنر و رسانه", "art_media.jpg", "آموزش گرافیک، رسانه و هنرهای تجسمی"),
    "computer": ("💻 کامپیوتر", "computer.jpg", "برنامه‌نویسی، شبکه، امنیت"),
    "economy": ("💰 اقتصاد و کوچینگ", "economy_coaching.jpg", "اقتصاد، بورس، کوچینگ"),
    "law": ("⚖️ حقوق و وکالت", "law_justice.jpg", "آموزش قوانین و آمادگی وکالت"),
    "science": ("🔬 علمی آزاد", "science_free.jpg", "دوره‌های عمومی و روش تحقیق"),
    "languages": ("🌍 زبان‌های خارجی", "languages.jpg", "انگلیسی، آلمانی، فرانسوی و..."),
}

# وقتی کاربر /start می‌زند
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("📞 ارسال شماره من", request_contact=True)]]
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("لطفاً برای ادامه شماره تماس خود را ارسال کنید:", reply_markup=reply)

# بعد از دریافت شماره تماس
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.message.from_user

    if not contact or not contact.phone_number:
        await update.message.reply_text("⚠️ خطا در دریافت شماره تماس، لطفاً دوباره تلاش کنید.")
        return

    # ارسال پیام مشخصات به گروه
    info = f"🆕 کاربر جدید:\n" \
           f"👤 {user.full_name}\n" \
           f"📱 {contact.phone_number}\n" \
           f"🆔 {user.id}\n" \
           f"🔗 @{user.username or 'ندارد'}"
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=info)

    # حذف کلید صفحه‌کلید شماره
    await update.message.reply_text("✅ شماره شما ثبت شد.", reply_markup=ReplyKeyboardRemove())

    # ارسال دکمه‌های دپارتمان
    keyboard = [
        [InlineKeyboardButton(title, callback_data=key)]
        for key, (title, _, _) in DEPARTMENTS.items()
    ]
    await update.message.reply_text(
        "لطفاً از بین دپارتمان‌ها یکی را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# وقتی کاربر روی یکی از دکمه‌ها کلیک کرد
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data

    if key in DEPARTMENTS:
        title, filename, caption = DEPARTMENTS[key]
        if os.path.exists(filename):
            with open(filename, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=query.message.chat.id,
                    photo=photo,
                    caption=f"{title}\n{caption}\n\n📞 برای کسب اطلاعات بیشتر ۰۳۵۳۸۲۱۱۱۰۰ تماس بگیرید."
                )
        else:
            await context.bot.send_message(
                chat_id=query.message.chat.id,
                text="⚠️ عکس مربوط به این دپارتمان یافت نشد."
            )

# تنظیم و اجرای ربات
def run_bot():
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app_bot.add_handler(CallbackQueryHandler(button_handler))
    app_bot.run_polling()

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))).start()
    run_bot()
