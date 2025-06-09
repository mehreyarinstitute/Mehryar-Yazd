async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    dept_data = departments.get(query.data)
    if not dept_data:
        await query.message.reply_text("اطلاعاتی یافت نشد.")
        return

    # مسیر فایل عکس
    image_path = dept_data["image"]
    description = dept_data["description"]
    phone = dept_data["phone"]

    caption = f"{query.data}\n\n{description}\n\n☎️ شماره موسسه: {phone}"

    # ارسال عکس همراه با توضیح
    try:
        with open(image_path, "rb") as img:
            await context.bot.send_photo(chat_id=query.message.chat.id, photo=img, caption=caption)
    except FileNotFoundError:
        await query.message.reply_text(f"❌ فایل عکس {image_path} یافت نشد.")
