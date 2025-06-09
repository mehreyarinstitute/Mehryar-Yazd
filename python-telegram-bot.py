import os
import pandas as pd
from flask import Flask
from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import threading

TOKEN = os.environ["TOKEN"]
ADMIN_IDS = [6441736006, 364551688]
GROUP_CHAT_ID = -1002095809427  # آی‌دی عددی گروه تلگرامی که لینک آن: https://t.me/+RFX8AaqzT_5jMDA0

user_data_file = "user_data.xlsx"
app = Flask(__name__)
registered_users = {}

if os.path.exists(user_data_file):
    df = pd.read_excel(user_data_file)
    registered_users = {int(row["user_id"]): row["phone"] for _, row in df.iterrows()}

@app.route('/ping')
def ping():
    return 'pong'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in registered_users:
        await send_departments_menu(update, context)
    else:
        keyboard = [[KeyboardButton("ارسال شماره ☎️", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("لطفاً شماره موبایل خود را ارسال کنید:", reply_markup=reply_markup)

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.message.from_user

    if user.id in registered_users:
        return

    phone = contact.phone_number
    registered_users[user.id] = phone

    # Save to Excel
    df = pd.DataFrame([{
        "user_id": user.id,
        "username": user.username or "",
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "phone": phone
    }])
    if os.path.exists(user_data_file):
        old_df = pd.read_excel(user_data_file)
        df = pd.concat([old_df, df], ignore_index=True)
    df.to_excel(user_data_file, index=False)

    # Send info to admin group
    info = f"🆕 کاربر جدید:\n👤 {user.full_name}\n📞 {phone}\n🔗 @{user.username or 'ندارد'}"
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=info)

    # Send Excel file
    await context.bot.send_document(chat_id=GROUP_CHAT_ID, document=open(user_data_file, "rb"))

    await update.message.reply_text("✅ شماره شما ثبت شد.", reply_markup=ReplyKeyboardRemove())
    await send_departments_menu(update, context)

async def send_departments_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎨 هنر و رسانه", callback_data="art_media")],
        [InlineKeyboardButton("💻 کامپیوتر", callback_data="computer")],
        [InlineKeyboardButton("💰 اقتصاد و کوچینگ", callback_data="economy_coaching")],
        [InlineKeyboardButton("⚖️ حقوق و وکالت", callback_data="law_justice")],
        [InlineKeyboardButton("🔬 علمی آزاد", callback_data="science_free")],
        [InlineKeyboardButton("🌍 زبان‌های خارجی", callback_data="languages")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.message.chat_id, text="دپارتمان مورد نظر را انتخاب کنید:", reply_markup=reply_markup)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    department = query.data
    captions = {
        "art_media": "🎨 دپارتمان هنر و رسانه\nآموزش‌های تخصصی در زمینه هنرهای تجسمی، طراحی، تدوین و رسانه\n📞 تماس: 03538211100",
        "computer": "💻 دپارتمان کامپیوتر\nبرنامه‌نویسی، شبکه، امنیت و آموزش نرم‌افزارهای کاربردی\n📞 تماس: 03538211100",
        "economy_coaching": "💰 دپارتمان اقتصاد و کوچینگ\nآموزش‌های اقتصادی، رشد مالی و مهارت‌های مربی‌گری فردی و سازمانی\n📞 تماس: 03538211100",
        "law_justice": "⚖️ دپارتمان حقوق و وکالت\nدروس حقوقی، آمادگی آزمون و آموزش‌های تخصصی در زمینه قوانین\n📞 تماس: 03538211100",
        "science_free": "🔬 دپارتمان علمی آزاد\nآموزش‌های متفرقه و عمومی برای رشد علمی در رشته‌های مختلف\n📞 تماس: 03538211100",
        "languages": "🌍 دپارتمان زبان‌های خارجی\nآموزش زبان‌های انگلیسی، فرانسه، آلمانی و غیره\n📞 تماس: 03538211100"
    }
    image_path = f"{department}.png"

    if os.path.exists(image_path):
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=open(image_path, "rb"), caption=captions[department])
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="عکس مربوطه یافت نشد.")

def run_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_buttons))
    application.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    print("ربات اجرا شد...")
    application.run_polling()

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8000)).start()
    run_bot()
