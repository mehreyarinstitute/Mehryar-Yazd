# bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

TOKEN = "توکن خودت را اینجا بگذار"

async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("پایتون", callback_data='python'),
            InlineKeyboardButton("هوش مصنوعی", callback_data='ai'),
        ],
        [
            InlineKeyboardButton("زبان", callback_data='language'),
            InlineKeyboardButton("رزین", callback_data='resin'),
        ],
        [
            InlineKeyboardButton("ارز دیجیتال", callback_data='crypto'),
            InlineKeyboardButton("نقاشی", callback_data='painting'),
        ],
        [
            InlineKeyboardButton("کامپیوتر", callback_data='computer')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("موضوع مورد علاقه‌ات را انتخاب کن:", reply_markup=reply_markup)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.run_polling()
