async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    dept_name = query.data
    dept_info = departments.get(dept_name)

    if dept_info:
        description = dept_info["description"]
        image_path = dept_info["image"]
        phone_number = dept_info["phone"]

        # ارسال عکس
        with open(image_path, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=query.message.chat.id,
                photo=photo,
                caption=f"{dept_name}\n\n{description}\n\n☎️ شماره موسسه: {phone_number}"
            )
    else:
        await context.bot.send_message(chat_id=query.message.chat.id, text="اطلاعاتی یافت نشد.")
