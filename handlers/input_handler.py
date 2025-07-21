from telegram import Update
from telegram.ext import ContextTypes
from notion.update_book import update_book_in_notion

async def input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting" not in context.user_data or "edit_book_id" not in context.user_data:
        return

    book_id = context.user_data["edit_book_id"]
    step = context.user_data["awaiting"]
    text = update.message.text.strip()

    if step == "score":
        context.user_data["new_score"] = text
        context.user_data["awaiting"] = "comment"
        await update.message.reply_text("Теперь введите комментарий:")
    elif step == "comment":
        score = context.user_data["new_score"]
        comment = text

        success = await update_book_in_notion(book_id, {
            "Score": {"select": {"name": score}},
            "Comments": {
                "rich_text": [{"type": "text", "text": {"content": comment}}]
            }
        })

        if success:
            await update.message.reply_text("✅ Оценка и комментарий сохранены!")
        else:
            await update.message.reply_text("❌ Ошибка при сохранении данных в Notion.")

        for key in ["awaiting", "edit_book_id", "new_score"]:
            context.user_data.pop(key, None)
