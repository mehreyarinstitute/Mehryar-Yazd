import os
import pandas as pd
from flask import Flask, request
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

ADMINS = [6441736006]
GROUP_CHAT_ID = -1002737227310
users_data = pd.DataFrame(columns=["user_id", "username", "phone"])

app = Flask(__name__)

# دپارتمان‌ها
departments = {
    "هنر و رسانه": {
        "description": "در این دپارتمان با تکنیک‌های هنری و رسانه‌ای آشنا خواهید شد. 📸🎨",
        "image": "art_media.jpg",
        "phone": "03538211100"
    },
    "کامپیوتر": {
        "description": "دپارتمان کامپیوتر شامل آموزش برنامه‌نویسی، شبکه و فناوری اطلاعات است. 💻🖥️",
        "image": "computer.jpg",
        "phone": "03538211100"
    },
    "اقتصاد و کوچینگ": {
        "description": "آموزش اصول اقتصاد، بازار و مهارت‌های کوچینگ فردی و سازمانی. 📈💼",
        "image": "economy_coaching.jpg",
        "phone": "03538211100"
    },
    "حقوق و وکالت": {
        "description": "با مفاهیم حقوقی و اصول وکالت حرفه‌ای در این دپارتمان آشنا شوید. ⚖️📚",
        "image": "law.jpg",
        "phone": "03538211100"
    },
    "علمی آزاد": {
        "description": "آموزش‌های متنوع علمی در زمینه‌های مختلف بدون محدودیت رشته. 🔬📘",
        "image": "science.jpg",
        "phone": "03538211100"
    },
    "زبان‌های خارجی": {
        "description": "یادگیری زبان‌های انگلیسی، آلمانی و فرانسه با جدیدترین متدها. 🌍🗣️",
        "image": "language.jpg",
        "phone": "03538211100"
    }
}

def get_main_menu():
    keyboard = [[InlineKeyboardButton(text=title, callback_data=title)] for title in departments.keys()]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if 'phone' not in context.user_data:
        button = KeyboardButton(text="📱 ارسال شماره تماس", request_contact=True)
        reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)
        await context.bot.send_message(chat_id=chat_id, text="لطفاً شماره تماس خود را ارسال کنید:", reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=chat_id, text="از دکمه‌های زیر یکی را انتخاب کنید:", reply_markup=get_main_menu())

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.effective_user

    phone = contact.phone_number
    user_id = user.id
    username = user.username or "بدون نام کاربری"

    if 'phone' not in context.user_data:
        context.user_data['phone'] = phone

        global users_data
        if not any(users_data['user_id'] == user_id):
            new_row = pd.DataFrame([[user_id, username, phone]], columns=["user_id", "username", "phone"])
            users_data = pd.concat([users_data, new_row], ignore_index=True)

            file_path = "users.xlsx"
            users_data.to_excel(file_path, index=False)

            await context.bot.send_document(chat_id=GROUP_CHAT_ID, document=open(file_path, 'rb'))
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"کاربر جدید ثبت شد ✅\nنام کاربری: @{username}\nشماره: {phone}")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="از دکمه‌های زیر یکی را انتخاب کنید:", reply_markup=get_main_menu())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    dept_name = query.data
    dept_info = departments.get(dept_name)

    if dept_info:
        description = dept_info["description"]
        image_path = dept_info["image"]
        phone = dept_info["phone"]

        if os.path.exists(image_path):
            with open(image_path, 'rb') as img:
                await context.bot.send_photo(chat_id=query.message.chat.id, photo=img)

        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"{dept_name}\n\n{description}\n\n☎️ شماره موسسه: {phone}"
        )
    else:
        await context.bot.send_message(chat_id=query.message.chat.id, text="دپارتمان پیدا نشد ❌")

@app.route(f"/{os.environ.get('BOT_TOKEN')}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), app_telegram.bot)
    await app_telegram.process_update(update)
    return "ok"

@app.route("/ping")
def ping():
    return "pong"

if __name__ == '__main__':
    from telegram.ext import Application
    import logging
    logging.basicConfig(level=logging.INFO)

    TOKEN = os.environ.get("BOT_TOKEN")
    PORT = int(os.environ.get("PORT", 8443))
    WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")

    app_telegram = ApplicationBuilder().token(TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app_telegram.add_handler(CallbackQueryHandler(handle_callback))

    if WEBHOOK_URL:
        app_telegram.bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")

    app.run(host="0.0.0.0", port=PORT)
