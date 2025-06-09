async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    dept_data = departments.get(query.data)
    if not dept_data:
        await query.message.reply_text("اطلاعاتی یافت نشد.")
        return

    image_path = dept_data["image"]  # نام فایل عکس مثلاً: art_media.jpg
    description = dept_data["description"]
    phone = dept_data["phone"]

    caption = f"{query.data}\n\n{description}\n\n☎️ شماره موسسه: {phone}"

    try:
        with open(image_path, "rb") as photo_file:
            await context.bot.send_photo(
                chat_id=query.message.chat.id,
                photo=photo_file,
                caption=caption
            )
    except FileNotFoundError:
        await query.message.reply_text(f"❌ عکس مربوط به این دپارتمان پیدا نشد: {image_path}")
