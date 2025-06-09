import os
import threading
from flask import Flask
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup,
                      KeyboardButton, ReplyKeyboardMarkup, Contact)
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          CallbackQueryHandler, ContextTypes, filters)
from openpyxl import Workbook, load_workbook

TOKEN = os.environ["TOKEN"]
EXCEL_FILE = "contacts.xlsx"
GROUP_CHAT_ID = -1002059821624  # آی‌دی عددی گروه ادمین (از t.me لینک استخراج شده)

# دپارتمان‌ها
DEPARTMENTS = {
    "art": ("🎨 هنر و رسانه", "art_media.png", "دپارتمان هنر و رسانه ارائه‌دهنده آموزش‌های تخصصی در زمینه‌های هنری، گرافیک، عکاسی و رسانه است."),
    "computer": ("💻 کامپیوتر", "computer.png", "در دپارتمان کامپیوتر، مهارت‌های برنامه‌نویسی، طراحی سایت، امنیت و شبکه آموزش داده می‌شود."),
    "economy": ("💰 اقتصاد و کوچینگ", "economy_coaching.png", "این دپارتمان شامل آموزش‌هایی در زمینه اقتصاد، بورس، کسب‌وکار و کوچینگ فردی است."),
    "law": ("⚖️ حقوق و وکالت", "law_justice.png", "در دپارتمان حقوق، مطالب مرتبط با وکالت، قوانین و حقوق عمومی تدریس می‌شود."),
    "science": ("🔬 علمی آزاد", "science_free.png", "دپارتمان علمی آزاد برای علاقه‌مندان به رشته‌های عمومی و دروس آزاد طراحی شده است."),
    "languages": ("🌐 زبان‌های خارجی", "languages.png", "در این دپارتمان، زبان‌های انگلیسی، آلمانی، فرانسوی و سایر زبان‌های زنده دنیا تدریس می‌شود.")
}

app = Flask(__name__)

@app.route('/ping')
def ping():
    return 'pong'

def contact_exists(user_id):
    if not os.path.exists(EXCEL_FILE):
        return False
    wb = load_workbook(EXCEL_FILE)
    ws = wb.active
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[1] == user_id:
            return True
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if contact_exists(user.id):
        await update.message.reply_text("✅ شماره شما قبلاً ثبت شده است.")
        await show_departments(update, context)
        return

    contact_button = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 ارسال شماره من", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text("برای ادامه، لطفاً شماره تماس خود را ارسال کنید:", reply_markup=contact_button)

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact: Contact = update.message.contact
    user = update.message.from_user

    if contact_exists(user.id):
        await update.message.reply_text("✅ شماره شما قبلاً ثبت شده است.")
        await show_departments(update, context)
        return

    if os.path.exists(EXCEL_FILE):
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.append(["نام", "آی‌دی عددی", "یوزرنیم", "شماره تماس"])

    ws.append([
        f"{user.first_name} {user.last_name or ''}",
        user.id,
        user.username or "ندارد",
        contact.phone_number
    ])
    wb.save(EXCEL_FILE)

    info = (
        f"📥 ثبت شماره جدید:
"
        f"👤 {user.first_name} {user.last_name or ''}\n🆔 {user.id}\n"
        f"🔗 @{user.username if user.username else 'ندارد'}\n"
        f"📞 {contact.phone_number}"
    )
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=info)
    await context.bot.send_document(chat_id=GROUP_CHAT_ID, document=open(EXCEL_FILE, "rb"))
    await update.message.reply_text("✅ شماره شما با موفقیت ثبت شد.")
    await show_departments(update, context)

async def show_departments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(title, callback_data=key)]
        for key, (title, _, _) in DEPARTMENTS.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("لطفاً دپارتمان مورد نظر را انتخاب کنید:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data
    if key in DEPARTMENTS:
        title, image_path, caption = DEPARTMENTS[key]
        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                await context.bot.send_photo(chat_id=query.message.chat.id, photo=photo, caption=f"{caption}\n\n📞 تماس با ما: 03538211100")
        else:
            await query.message.reply_text("متاسفانه تصویر مربوطه یافت نشد.")

def run_bot():
    app_telegram = ApplicationBuilder().token(TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app_telegram.add_handler(CallbackQueryHandler(button_handler))
    print("ربات در حال اجراست...")
    app_telegram.run_polling()

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=PORT)).start()
    run_bot()
