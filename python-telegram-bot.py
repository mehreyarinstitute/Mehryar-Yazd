from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import pandas as pd
import os

# لیست ادمین‌ها (آیدی عددی تلگرام)
ADMINS = [6441736006]

# آیدی عددی گروه تلگرام
GROUP_CHAT_ID = -1002737227310

# دیتافریم برای ذخیره شماره‌ها
users_data = pd.DataFrame(columns=["user_id", "username", "phone"])

# دپارتمان‌ها و توضیحات
departments = {
    "هنر و رسانه": "در این دپارتمان با تکنیک‌های هنری و رسانه‌ای آشنا خواهید شد. 📸🎨",
    "کامپیوتر": "دپارتمان کامپیوتر شامل آموزش برنامه‌نویسی، شبکه و فناوری اطلاعات است. 💻🖥️",
    "اقتصاد و کوچینگ": "آموزش اصول اقتصاد، بازار و مهارت‌های کوچینگ فردی و سازمانی. 📈💼",
    "حقوق و وکالت": "با مفاهیم حقوقی و اصول وکالت حرفه‌ای در این دپارتمان آشنا شوید. ⚖️📚",
    "علمی آزاد": "آموزش‌های متنوع علمی در زمینه‌های مختلف بدون محدودیت رشته. 🔬📘",
    "زبان‌های خارجی": "یادگیری زبان‌های انگلیسی، آلمانی و فرانسه با جدیدترین متدها. 🌍🗣️"
}

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton(text=title, callback_data=title)] for title in departments.keys()
    ]
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
            users_data = pd.concat([
                users_data,
                pd.DataFrame([[user_id, username, phone]], columns=["user_id", "username", "phone"])
            ], ignore_index=True)

            # ذخیره در فایل Excel
            file_path = "users.xlsx"
            users_data.to_excel(file_path, index=False)

            # ارسال فایل به گروه
            await context.bot.send_document(chat_id=GROUP_CHAT_ID, document=open(file_path, 'rb'))

            # ارسال پیام مشخصات به گروه
            await context.bot.send_message(chat_id=GROUP_CHAT_ID,
                                           text=f"کاربر جدید ثبت شد ✅\nنام کاربری: @{username}\nشماره: {phone}")

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="از دکمه‌های زیر یکی را انتخاب کنید:",
                                   reply_markup=get_main_menu())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    dept_name = query.data
    description = departments.get(dept_name, "اطلاعاتی یافت نشد")

    await context.bot.send_message(chat_id=query.message.chat.id,
                                   text=f"{dept_name}\n\n{description}\n\n☎️ شماره موسسه: 03538211100")

if __name__ == '__main__':
    import logging
    from telegram.ext import CallbackQueryHandler

    logging.basicConfig(level=logging.INFO)

    TOKEN = os.environ.get("BOT_TOKEN")  # توکن بات رو از متغیر محیطی بگیر

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(CallbackQueryHandler(handle_callback))

    app.run_polling()
